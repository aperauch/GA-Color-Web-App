#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from itertools import imap
import operator, random, webapp2, os, jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainHandler(webapp2.RequestHandler):
        
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render())

class SimpleColorGA(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('blanksimple.html')
        self.response.write(template.render())
        
    def post(self):
        'Variables needed for HTML template'
        popSize = int(self.request.get("popSize"))
        numGens = int(self.request.get("numGens"))
        scaleSize = int(self.request.get("scaleSize"))
        
        'Variables needed for Python processing'
        targetColor = str(self.request.get("targetColor"))
        binaryTargetColor = self.convertHexadecimalToBinary(targetColor)
        print binaryTargetColor
        maxDiff = int(self.request.get("maxDiff"))
        
        'Begin processing to create evolution from target color'
        completeEvolution = []
        startingPopulation = self.createPopulation(popSize)
        nextGen = self.convertDecimalToBinary(startingPopulation)
        
        for i in range(numGens):
            fittest = self.getFittestIndividuals(nextGen, binaryTargetColor, maxDiff)
            crossed = self.crossover(fittest)
            nextGen = self.mutate(crossed, 0)
            offspring = self.convertBinaryToHexadecimal(nextGen)
            completeEvolution.append(offspring)            
            
        'Find the largest population size in the evolution'
        largestPop = 0;
        emptyPops = 0
        totalGens = len(completeEvolution)
        for i in completeEvolution:
            if (len(i) < 1):
                emptyPops += 1 
            if (len(i) > largestPop):
                largestPop = len(i)
                    
        canvasWidth = largestPop * scaleSize
        canvasHeight = (totalGens - emptyPops) * scaleSize
          
        template_values = {
                           "targetColor" : targetColor,
                           "canvasWidth" : canvasWidth,
                           "canvasHeight" : canvasHeight,
                           "popSize" : popSize,
                           "numGens" : numGens,
                           "scaleSize" : scaleSize,
                           "maxDiff" : maxDiff,
                           "largestPop" : largestPop,
                           "evolution" : completeEvolution
                           }
         
        template = JINJA_ENVIRONMENT.get_template('simple.html')
        self.response.write(template.render(template_values))
        
    def createPopulation(self, size):
        newPopulation = []

        if size > 0:
            for i in range(size):
                newPopulation.append(random.sample(range(256), 3))
                
        return newPopulation
    
    def convertDecimalToBinary(self, population):
        listOfColors = []
        
        for i in population:
                byte = ''
                for j in range(len(i)):  
                    tempByte = str(bin(i[j])[2:])
                    if (len(tempByte) < 8):
                        padding = ""
                        for k in range(8-len(tempByte)):
                            padding += "0"
                        tempByte = padding + tempByte
                    byte += tempByte
                listOfColors.append(byte)
                    
        return listOfColors
    
    def convertBinaryToDecimal(self, population):
        listOfColors = []
        
        for i in population:
            r = int(i[:8], 2)
            g = int(i[8:16], 2)
            b = int(i[16:24], 2)
            individual = [r, g, b]
            listOfColors.append(individual)
        
        return listOfColors
    
    def convertBinaryToHexadecimal(self, population):
        listOfColors = []
        
        for i in population:
            color = hex(int(i, 2))
            color = color.replace('0x', '#')
            listOfColors.append(color)
        
        return listOfColors
    
    def convertHexadecimalToBinary(self, hexColor):
        hexColor = hexColor.replace('#', '')
        hexColor = hexColor.replace('0x', '')
        binaryColor = bin(int(hexColor, 16))[2:].zfill(24)
        return binaryColor
        
    def getFittestIndividuals(self, popColors, targetColor, maxDifference):
        ne = operator.ne
        scoresList = []
        fittestPopulation = []
        
        for c in popColors:
            score = sum(imap(ne, c, targetColor))
            if(score <= maxDifference):
                scoresList.append(score)
                fittestPopulation.append(c)
    
        return fittestPopulation
    
    def crossover(self, population):
        popSize = len(population)
        crossedPopulation = []
        
        while (popSize >= 2):
            r1 = random.randint(0, popSize - 1)
            parent1 = population.pop(r1)
            popSize = len(population)
            r2 = random.randint(0, popSize - 1)
            parent2 = population.pop(r2)
            
            crossPoint = random.randint(1, 23)
            
            child1 = parent1[:crossPoint]
            child1 += parent2[crossPoint:]
            child2 = parent2[:crossPoint]
            child2 += parent1[crossPoint:]
            
            crossedPopulation.append(child1)
            crossedPopulation.append(child2)
            
            popSize = len(population)
            
        return crossedPopulation
    
    def mutate(self, population, rate):
        mutatedPopulation = []
        if (rate == 0 or rate == None):
            rate = random.random()
        
        for i in range(len(population)):
            mutate = random.random()
            
            if (mutate > rate):
                index = random.randint(0, 23)
                individual = list(population[i])
                
                if (individual[index] == '0'):
                    individual[index] = '1'
                else:
                    individual[index] = '0'
               
                mutatedPopulation.append(''.join(individual))
                 
        return population

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/simple', SimpleColorGA)
], debug=True)