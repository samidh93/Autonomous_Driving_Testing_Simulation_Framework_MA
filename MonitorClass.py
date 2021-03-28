import sys
import argparse
import csv
import os
import bagpy
from bagpy import bagreader
import pandas as pd
import numpy as np
from collections import defaultdict, Iterable
from pyModelChecking import *
from pyModelChecking.CTLS import *


# ModelChecker.py
description = 'ModelChecker.py |\n \
Read bag file, extract data by topic |\n \
Create a krypke Structure for model |\n \
Model checking with CTL* |\n \
topics: i >=0 [/vehicle{i}/ENV/propositions, /vehicle{i}/VEH/ax, /vehicle{i}/odom, /vehicle{i}/traffic]|\n \
shell: python3 ModelChecker.py -i|--input inputfile.bag -o|--output outputfile.txt -t|--topic |\n \
example: python3 ModelChecker.py -i inputfile.bag -o outputfile.txt -t /vehicle0/ENV/propositions /vehicle0/VEH/ax /vehicle0/odom /vehicle0/traffic\n \
Author: Sami Dhiab \n \
Topics to analyse: \n \
topic1 = ''/vehicle0/ENV/propositions'' -> Criteria {in collision, near goal} \n \
topic2 = ''/vehicle0/VEH/ax'' -> Criteria {Ego acceleration, deceleration} \n \
topic3 = ''/vehicle0/odom'' -> Criteria {Ego position(x,y), Ego Speed(x,y), ...} \n \
topic4 = ''/vehicle0/traffic''-> Criteria {sumo ID, sumo position, sumo Speed, signal status(brake, left, right indicator) ...} \n \
Kriteria to check: \n \
-twist: Ego Speed \n \
-ax: Ego Acceleration, Deceleration Rate \n \
-safety Separation Distance(gap) Lateral/longitudnal \n \
-Signal Status (brake is on, left or right indicator)'

IN_COLLISION = 'IN_COLLISION'
NEAR_GOAL = 'NEAR_GOAL'
EGO_SPEED = 'EGO_SPEED'
MAX_SPEED = 30
SAFE_DISTANCE_X = 'SAFE_DISTANCE_X'
SAFE_DISTANCE_Y = 'SAFE_DISTANCE_Y'
Deceleration = 'Deceleration'
p = 'p'  # IN Collision
q = 'q'  # Near goal
v = 'v'  # EGO_SPEED
x = 'x'  # X_Safe_dis
y = 'y'  # Y_SAfe_dis
a = 'a'  # EGO_ax


class Monitor:
    """Class for monitoring a model\n
    *Read bag file, extract data by topic\n
    *Creating a krypke Structure for model\n
    *Model checking with CTL* \n
    *Args: see constructor: Monitor.__init__
    """

    def __init__(self, inputfile, outputfile, topic):
        """Monitor constructor
        Args:\n
            inputfile (.bag): choose a bag file to treat\n
            outputfile (.txt): choose a file to write result to\n
            topic (string): choose a topic string to parse
        """
        self.inputfile = inputfile
        self.topic = topic
        self.outputfile = outputfile
        self.Result = None

    def ReadBagFileByTopic(self, inputfile, topic):
        """Read bag file and filter by topic\n
        write content to csv file\n
        get the content in pandas dataframe"""

        b = bagreader(inputfile)
        data = b.message_by_topic(topic)
        dataframe = pd.read_csv(data)

        return dataframe

    @staticmethod
    def WriteResultToFile(outputfile, result):
        """write test Result to a file"""
        with open(outputfile, 'w') as the_file:
            if result:
                print('test passed, Result saved to: ',
                      os.path.realpath(outputfile))
                the_file.write('test passed\n')

            else:
                print('test failed, Result saved to: ',
                      os.path.realpath(outputfile))
                the_file.write('test failed\n')

    def DataFrameExtractByTerm(self, BaseDf, Term, Value):
        """Extract dataframe from dataframe
        by specifiying Term and Value
        resetting index from zero"""

        if Value is None:
            ExtractedDf = BaseDf[[Term]]
        else:
            ExtractedDf = BaseDf.loc[BaseDf[Term] == Value]
            # Reset indexing from zero
            ExtractedDf = ExtractedDf.reset_index(drop=True)

        return ExtractedDf

    def GetColumnIndex(self, Df, ColumnName):
        """return the Index of column in dataframe """
        IndexColumn = Df.columns.get_loc(ColumnName)

        return IndexColumn

    def CheckDecelerationToBrakeStatus(self, brakeStatusOn, acutalAcceleration, lastAcceleration):
        """Check deceleration rate based on brake light status"""
        if brakeStatusOn == True:  # if brakelight is on
            if (acutalAcceleration - lastAcceleration) < 0:
                return True
            else:
                return False

    def GenerateKrypkeFromDataFrame(self, DataFrame, PropositionString, AtomicProposition):
        """Iterate dataframe and update propositions
        generate krypke from propositions"""
        from distutils.util import strtobool
        H = {}
        R = [(0, 0)]
        L = dict()
        Brake = None

        if PropositionString == SAFE_DISTANCE_X:
            print('Checking longitudinal safe distance..')
        if PropositionString == SAFE_DISTANCE_Y:
            print('Checking lateral safe distance..')
        if PropositionString == Deceleration:
            print('Checking Deceleration if brake light is on..')
            b = self.GetColumnIndex(DataFrame, 'brakeLightStatusOn')
            l = [i for i, x in enumerate(b) if x]
            a = self.GetColumnIndex(DataFrame, 'Ego.ax')
        if PropositionString == EGO_SPEED:
            print('Checking Speed limit..')
        if PropositionString == IN_COLLISION:
            print('Checking if there is a Collision..')
        if PropositionString == NEAR_GOAL:
            print('Checking if Goal is reached..')

        if DataFrame.dropna().empty:
            print('empty dataframe, nothing to create..')
            return False

        for i, j in DataFrame.iterrows():
            B = (i, i+1)
            # AtomicProposition should be String like 'p', 'q'..
            p = str(AtomicProposition)

            if PropositionString == IN_COLLISION or PropositionString == NEAR_GOAL:
                t = self.GetColumnIndex(DataFrame, 'term')
                v = self.GetColumnIndex(DataFrame, 'value')
                if str(j[t]) == PropositionString and j[v] == False:  # incollision is false
                    H = {i: set([Not(p)])}

                elif str(j[t]) == PropositionString and j[v] == True:  # incollision is true
                    H = {i: set([p])}

            elif PropositionString == EGO_SPEED:
                e = self.GetColumnIndex(DataFrame, 'twist.twist.linear.x')
                if int(j[e]) > MAX_SPEED:  # ego_speed > MAx_speed -> p false
                    H = {i: set([Not(p)])}

                elif int(j[e]) <= MAX_SPEED:  # ego_speed =< MAx_speed -> p true
                    H = {i: set([p])}
            elif PropositionString == SAFE_DISTANCE_X:
                for index, value in enumerate(self.GetColumnIndex(DataFrame, 'POV_X')):
                    if value:
                        if pd.isnull(j[self.GetColumnIndex(DataFrame, 'Ego.x')]) or pd.isnull(j[self.GetColumnIndex(DataFrame, 'Ego.Vx')]) or pd.isnull(j[index]):
                            continue
                        if self.CheckSafeDistance(
                                j[self.GetColumnIndex(DataFrame, 'Ego.Vx')], j[self.GetColumnIndex(DataFrame, 'Ego.x')], j[index]):
                            H = {i: set([p])}
                        else:
                            H = {i: set([Not(p)])}
            elif PropositionString == SAFE_DISTANCE_Y:
                for index, value in enumerate(self.GetColumnIndex(DataFrame, 'POV_Y')):
                    if value:
                        if pd.isnull(j[self.GetColumnIndex(DataFrame, 'Ego.y')]) or pd.isnull(j[index]):
                            continue
                        if self.CheckLateralDistance(j[self.GetColumnIndex(DataFrame, 'Ego.y')], j[index]):
                            H = {i: set([p])}
                        else:
                            H = {i: set([Not(p)])}

            elif PropositionString == Deceleration:
                if i == 0:
                    continue
                for idx in l:
                    if pd.isnull(j[idx]):
                        continue
                    if strtobool(j[idx]):
                        Brake = True
                    else:
                        Brake = False
                if self.CheckDecelerationToBrakeStatus(Brake, j[a], DataFrame.at[i-1, 'Ego.ax']):
                    H = {i: set([p])}
                elif self.CheckDecelerationToBrakeStatus(Brake, j[a], DataFrame.at[i-1, 'Ego.ax']) is False:
                    H = {i: set([Not(p)])}

            if i == DataFrame.index[-1]:
                B = (i, i)

            R.append(B)
            L.update(H)

        if H == {}:
            R = []
            L = dict()
            print('no data found, nothing to create..')
            return False

        K = Kripke(R=R, L=L)
        print('Kripke Structure created.')
        return K

    def FullMergeSet(self, R1, R2):
        """Merge content of different sets
        using the larger set"""
        if len(R1) > len(R2):
            R = R1
        else:
            R = R2
        return R

    def FullMergeDict(self, L1, L2):
        """Merge value of multiple dictionaries
        using the same key to new dict"""
        L = defaultdict(list)
        for dct in [L1, L2]:
            for k, v in dct.items():
                if isinstance(v, Iterable):
                    L[k].extend(v)
                else:
                    L[k].append(v)
        return L

    def MergeKrypke(self, K1, K2):
        """Merge content of two Krypke Structures
        by merging sets and dicts"""
        R1 = K1.transitions()
        R2 = K2.transitions()
        L1 = K1.labelling_function()
        L2 = K2.labelling_function()

        K = Kripke(R=self.FullMergeSet(R1, R2), L=self.FullMergeDict(L1, L2))
        return K

    def GetFormula(self, PropositionSet, AtomicProposition):
        """Get the right formula for a defined proposition"""
        p = AtomicProposition
        phi = A(G(Not(p)))  # phi: for all paths always not true
        # psi: for all paths exist in future a path and from this path always true
        psi = A(E(G(F(p))))
        taw = A(G(p))  # taw: true for all paths always
        omega = A(G(p))  # omega: always true for all paths
        gammma = A(G(p))  # gamma: always true for all paths
        Lambda = A(G(p))  # lambda: always true for all paths
        if PropositionSet == IN_COLLISION:
            return phi
        elif PropositionSet == NEAR_GOAL:
            return psi
        elif PropositionSet == EGO_SPEED:
            return taw
        elif PropositionSet == SAFE_DISTANCE_X:
            return omega
        elif PropositionSet == SAFE_DISTANCE_Y:
            return gammma
        elif PropositionSet == Deceleration:
            return Lambda

    def CheckModel(self, K, F):
        """ Check the model of a krypke structure by a defined formula
        return the states that satisfies that formula"""

        m = modelcheck(K, F)
        if len(m) == len(K.labelling_function()):
            print(
                "The Kripke Structure satisfies the defined formula, saving test result")
            self.Result = True

        else:
            print(
                "The Kripke Structure doesn't satisfy the defined formula, saving test result")
            self.Result = False

        return m

    def CombineFormulas(self, Formula1, Formula2):
        """Combine two Formulas with And to build a general Formula"""
        Combined = And(Formula1, Formula2)
        return Combined

    def CheckSafeDistance(self, SpeedEgo, PosEgo, PosPov):
        """Check Longitudinal Safe Distance between Ego and POVs
        Can be upgraded regarding ODD"""
        s = SpeedEgo
        xEgo = PosEgo
        xPov = PosPov
        Delta = abs(xEgo-xPov)
        # check if speed smaller than 15m/s or 50 km/h inside urban (for 50km/h distance should be 15m)
        if s <= 15:
            SafeDistance = int((s*3.6) / 3.33)
            if Delta >= SafeDistance:
                # print('Ego Speed:', s, 'm/s, Position Ego:', xEgo, 'm, Position POV:', xPov,
                #      'm, Safe Distance keeped:', SafeDistance, 'm, actual Distance:', Delta, 'm')
                return True
            elif Delta < SafeDistance:
                # print('Ego Speed:', s, 'm/s, Position Ego:', xEgo, 'm, Position POV:', xPov,
                #      'm, Safe Distance required:', SafeDistance, 'm, actual Distance:', Delta, 'm')
                return False

        # check if speed bigger than 15m/s or 50 km/h outside urban (for 100km/h distance should be 50m)
        else:
            SafeDistance = int((s*3.6) / 2)
            if Delta >= SafeDistance:
                # print('Ego Speed:', s, 'm/s, Position Ego:', xEgo, 'm, Position POV:', xPov,
                #      'm, Safe Distance keeped:', SafeDistance, 'm, actual Distance:', Delta, 'm')
                return True
            elif Delta < SafeDistance:
                # print('Ego Speed:', s, 'm/s, Position Ego:', xEgo, 'm, Position POV:', xPov,
                #      'm, Safe Distance required:', SafeDistance, 'm, actual Distance:', Delta, 'm')
                return False

    def CheckLateralDistance(self, YEgo, YPov):
        """Check Lateral Safe Distance between Ego and POVs
        Can be upgraded regarding ODD"""
        Delta = abs(YEgo-YPov)
        SafeLateral = 1.5  # depending on object classification(0,5->1,5)
        if Delta >= SafeLateral:
            # print('Safe Lateral Distance keeped: ', Delta, 'm')
            return True
        elif Delta < SafeLateral:
            # print('Safe Distance required: ', SafeLateral,
            #      'm, actual Distance: ', Delta, 'm')
            return False

    def ConvertStringListToDataframe(self, dataframe):
        """Convert list of strings like json format
        inside a Dataframe to a sorted Dataframe"""
        datas = []
        for index, value in dataframe.iterrows():
            data_array = dataframe.iloc[index, 0].split()
            datas.extend(data_array)
        Px = []
        Py = []
        ID = []
        Vx = []
        BrakeStatus = []
        for i, data in enumerate(datas):
            if data == 'position:':
                x = float(datas[i+2])
                Px.append(x)
                y = float(datas[i+4])
                Py.append(y)
            if data == 'linear:':
                v = float(datas[i+2])
                Vx.append(v)
            if data == 'brakeLightOn:':
                Brake = datas[i+1]
                BrakeStatus.append(Brake)
            if data == 'trackingID:':
                t = int(datas[i+1])
                ID.append(t)
        df = pd.DataFrame(ID, columns=['POV_ID'])
        df['POV_X'] = Px
        df['POV_Y'] = Py
        df['POV_Vx'] = Vx
        df['brakeLightStatusOn'] = BrakeStatus
        return df

    def FilterAndJoinPOVs(self, dataset):
        """ extract POVs dataframe filtered
        by ID, join dataframes together for next step"""
        max_col = (dataset["POV_ID"]).max()
        ID_max = max_col % 1000
        #Columns = ['POV_ID_'+str(x) for x in range(ID_max)]
        list_df = []
        for i in range(ID_max):
            extracted_df = self.DataFrameExtractByTerm(
                dataset, 'POV_ID', 1000+i)
            list_df.append(extracted_df)
        joined_df = pd.concat(list_df, axis=1, join="outer")
        return joined_df


class Analyser:

    """Class for Parsing Arguments
    and analysing all topics from command line"""

    def __init__(self):
        self.inputfile = None
        self.outputfile = None
        self.topics = None
        self.results = []

    def ParseArgument(self):
        """Arguments parsing and storing in class variables"""

        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('-i', '--input', type=str,
                            help='select a bag file')
        parser.add_argument('-o', '--output', type=str,
                            help='write result to a file')
        parser.add_argument('-t', '--topics', nargs='+',
                            type=str, help='select topics from list, see help for more infos')

        args = parser.parse_args()
        print('Parsing Arguments ..')
        self.inputfile = args.input
        self.outputfile = args.output
        self.topics = args.topics

    def AnalyseTopics(self):
        """ iterarte throw al topics from the list"""
        for i in range(50):
            for topic in self.topics:
                if topic == '/vehicle'+str(i)+'/ENV/propositions':
                    print('Analysing first topic:', topic)
                    M = Monitor(self.inputfile, self.outputfile, topic)
                    df = M.ReadBagFileByTopic(self.inputfile, topic)
                    print('extracting topic from bag file')
                    df1 = M.DataFrameExtractByTerm(df, 'term', IN_COLLISION)
                    df2 = M.DataFrameExtractByTerm(df, 'term', NEAR_GOAL)
                    K1 = M.GenerateKrypkeFromDataFrame(df1, IN_COLLISION, p)
                    K2 = M.GenerateKrypkeFromDataFrame(df2, NEAR_GOAL, q)
                    if K1 is False:
                        print(
                            'cannot check model for collision, either dataframe is empty or no relevant data found')
                    if K2 is False:
                        print(
                            'cannot check model for goal, either dataframe is empty or no relevant data found')
                    if K1 is not False:
                        phi = M.GetFormula(IN_COLLISION, p)
                        print('The No Collision Formula is: ', phi)
                        M.CheckModel(K1, phi)
                        self.results.append(M.Result)
                    if K2 is not False:
                        psi = M.GetFormula(NEAR_GOAL, q)
                        print('The Goal Achieving Formula is: ', psi)
                        M.CheckModel(K2, psi)
                        self.results.append(M.Result)

                elif topic == '/vehicle'+str(i)+'/VEH/ax':
                    print('Analysing second topic:', topic)
                    N = Monitor(self.inputfile, self.outputfile, topic)
                    df = N.ReadBagFileByTopic(self.inputfile, topic)
                    ax_df = (N.DataFrameExtractByTerm(df, 'data', None)
                             ).rename(columns={"data": "Ego.ax"})

                elif topic == '/vehicle'+str(i)+'/odom':
                    print('Analysing third topic:', topic)
                    P = Monitor(self.inputfile, self.outputfile, topic)
                    df = P.ReadBagFileByTopic(self.inputfile, topic)
                    posx_df = P.DataFrameExtractByTerm(
                        df, 'pose.pose.position.x', None)
                    posy_df = P.DataFrameExtractByTerm(
                        df, 'pose.pose.position.y', None)
                    twistx_df = P.DataFrameExtractByTerm(
                        df, 'twist.twist.linear.x', None)
                    twisty_df = P.DataFrameExtractByTerm(
                        df, 'twist.twist.linear.y', None)
                    Ego_df = pd.DataFrame(posx_df.values, columns=['Ego.x'])
                    Ego_df['Ego.y'] = posy_df.values
                    Ego_df['Ego.Vx'] = twistx_df.values
                    Ego_df['Ego.Vy'] = twisty_df.values
                    Kv = P.GenerateKrypkeFromDataFrame(twistx_df, EGO_SPEED, v)
                    if Kv is False:
                        print(
                            'cannot check model for speed, either dataframe is empty or no relevant data found')
                    if Kv is not False:
                        taw = P.GetFormula(EGO_SPEED, v)
                        print('The Speed Limit Formula is: ', taw)
                        P.CheckModel(Kv, taw)
                        self.results.append(P.Result)

                elif topic == '/vehicle'+str(i)+'/traffic':
                    print('Analysing fourth topic:', topic)
                    T = Monitor(self.inputfile, self.outputfile, topic)
                    print('extracting data from bag file..')
                    dt = T.ReadBagFileByTopic(self.inputfile, topic)
                    dx = T.DataFrameExtractByTerm(dt, 'data', None)
                    print('converting json data to dataframe..')
                    dataset = T.ConvertStringListToDataframe(dx)
                    if dataset.empty:
                        print('dataframe is empty, skipping..')
                        break
                    traffic_data = T.FilterAndJoinPOVs(dataset)
                    print('Creating final full dataset..')
                    full_set = pd.concat(
                        [Ego_df, ax_df, traffic_data], axis=1, join="outer")
                    Sx = T.GenerateKrypkeFromDataFrame(
                        full_set, SAFE_DISTANCE_X, x)
                    if Sx is False:
                        print(
                            'cannot check model for x axis safe distance, either dataframe is empty or no relevant data found')
                    if Kv is not False:
                        omega = T.GetFormula(SAFE_DISTANCE_X, x)
                        print('The Longitudinal Safe Distance Formula is: ', omega)
                        T.CheckModel(Kv, omega)
                        self.results.append(T.Result)

                    Sy = T.GenerateKrypkeFromDataFrame(
                        full_set, SAFE_DISTANCE_Y, y)
                    if Sy is False:
                        print(
                            'cannot check model for y axis safe distance, either dataframe is empty or no relevant data found')
                    if Sy is not False:
                        gamma = T.GetFormula(SAFE_DISTANCE_Y, y)
                        print('The Lateral Safe Distance Formula is: ', gamma)
                        T.CheckModel(Sy, gamma)
                        self.results.append(T.Result)

                    Ka = T.GenerateKrypkeFromDataFrame(
                        full_set, Deceleration, a)
                    if Ka is False:
                        print(
                            'cannot check model for brake deceleration, either dataframe is empty or no relevant data found')
                    if Ka is not False:
                        Lambda = T.GetFormula(Deceleration, a)
                        print('The Lateral Safe Distance Formula is: ', Lambda)
                        T.CheckModel(Ka, Lambda)
                        self.results.append(T.Result)

        print('checking overall test Result..')
        if all(self.results):
            Monitor.WriteResultToFile(self.outputfile, True)
        else:
            Monitor.WriteResultToFile(self.outputfile, False)
