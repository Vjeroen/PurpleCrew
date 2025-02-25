#!/usr/bin/env python
from random import randint
from crewai.flow import Flow, listen, start
import sys
import warnings
from pydantic import BaseModel

#Import all the individual crew for our floew
from crews.redteamcrew.redteamcrew import RedTeamCrew
from crews.blueteamcrew.blueteamcrew import Blueteamcrew
from crews.itopscrew.itopscrew import Itopscrew


class PurpleCrew(BaseModel):
    sentence_count: int = 1
    adversary: str = ""
    redteamcrew: str = ""
    filepath: str = ""
    inputs:str =""
    warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

class PurpleCrew(Flow[PurpleCrew]):

    @start()
    def define_adversary(self):
        print("Starting our Purple Team Crew - Sending Information to Red Team Crew:")
        #defining the state that can be shared between the crews 
        self.state.sentence_count = randint(1, 5)
        self.state.adversary = ""
        self.state.file_path = '' 
        self.state.inputs = "APT28-Center-of-Storm-2017.pdf"

    @listen(define_adversary)
    def start_analysis(self):
        print("Red Team starts working with the provided adversary or adds the PDF file details to local RAG for analysis")
        #self.state.filepath= 'documents/APT28-Center-of-Storm-2017.pdf'
        redteamresult = (
            RedTeamCrew()
            .crew()
            .kickoff(inputs=self.state.inputs)
        )
        print(redteamresult)
        self.state.redteamcrew = redteamresult.raw

    #@listen(generate_poem)
    #def save_poem(self):
        #print("Saving poem")
        #with open("poem.txt", "w") as f:
            #f.write(self.state.poem)
    

def kickoff():
    purplecrew = PurpleCrew()
    user_input = input("Enter your question: ")
    inputs = {
        'input': user_input
    }
    redteamresult = (
            RedTeamCrew()
            .crew()
            .kickoff(inputs=inputs)
    )
    print(redteamresult)
    #.state.redteamcrew = redteamresult.raw

def plot():
    pruplecrew = PurpleCrew()
    pruplecrew.plot()

if __name__ == "__main__":
    kickoff()
