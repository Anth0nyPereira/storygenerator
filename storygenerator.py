import random as rd
import spacy
from spacy.cli import download


class StoryGrammar:
    """ Basic operations on a grammar to support story generation """
    def __init__(self):
        self.rules = {'nothing': ['Define grammar rules']}

    def clear(self):
        self.rules = {'nothing': ['Define grammar rules']}

    def autopopulate(self, filename):
        """

        :param filename:
        :return:
        """

        grammarpopulatort = SpacyGrammarPopulator()

        grammarpopulatort.populate(self, filename)

        # just check the end result
        for r in self.rules:
            print(f'{r}\n')
            print(self.rules[r])


    def addrule(self, rulename, rulecontent):
        """
        Add a rule to the grammar. At this point it is not very coherent
        since it basically adds to the rule every time it is invoked. So,
        it does not allow replacement... not critical for first examples.


        :param rulename:
        :param rulecontent:
        :return:
        """
        rulename = f'*{rulename.upper()}*'

        if rulename in self.rules:
            self.rules[rulename].add(rulecontent)
        else:
            self.rules[rulename] = set(rulecontent)

    def isrule(self, rulename):
        """
        check if a rule token exists

        :param rulename:
        :return:
        """
        if f'*{rulename}*' in self.rules:
            return True
        return False

    def expand(self, entrypoint):
        """
        Expand a grammar sequence by replacing grammar tokens

        :param entrypoint:
        :return:
        """
        entrypoint = f'*{entrypoint.upper()}*'
        result = self.__inner_expand(entrypoint)
        return result

    def __inner_expand(self, entrypoint):
        """
        Replacing grammar tokens in a recursive manner. It stops if no replacement is made in current pass.

        :param entrypoint:
        :return:
        """
        changes = False
        splitEntry = entrypoint.split()
        rd.seed()

        for idx, element in enumerate(splitEntry):

            # this enables having a period next to a grammar token, e.g., *VERB* *OBJECT*. <-
            ponctuation = ('.', ',', '?', '!', ';')
            if element.endswith(ponctuation):
                terminator = element[-1]
                element = element.replace(terminator, '')
            else:
                terminator = ''

            if element in self.rules:
                splitEntry[idx] = self.getRandomItem(self.rules[element]) + terminator  # random does not work on sets
                changes = True

        result = ' '.join(splitEntry)
        if changes:
            result = self.__inner_expand(result)

        return result

    def getRandomItem(self, ruleitems):
        """
        This was put in a different method, so it may eventually evolve into
        a more complex approach with some rules

        :param ruleitems:
        :return:
        """
        choice = rd.choice(tuple(ruleitems))    # ruleitems is a set; choice does not work on sets; converting to tuple
        return choice


class SpacyGrammarPopulator:
    """
    This class can populate a story grammar from a file. It uses spacy to tokenize the file contents and defines
    rules based on that
    """
    def __init__(self):
        download("en_core_web_md")

    def populate(self, grammar: StoryGrammar, filename: str):
        """
        Uses spacy to tokenize text from filename and create and populate
        a set of grammar tokens concerning verbs, nouns, etc.

        https://spacy.io/models/en#en_core_web_md


        :param grammar:
        :param filename:
        :return:
        """
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read();

        print('Loading the language model...')
        nlp = spacy.load('en_core_web_md')
        tokens = nlp(text)

        # for verbs
        for t in tokens:
            print(t, t.pos_, t.dep_, t.head, t.head.i)
            if t.pos_ == 'VERB':

                morph = t.morph
                verbForm = ''.join(morph.get('VerbForm'))
                verbTense = ''.join(morph.get('Tense'))
                print(f'verb {verbForm} {verbTense}')
                rulename = f'VERB_{verbForm}_{verbTense}'

                for anc in t.ancestors:
                    print('*', anc.text, anc.pos_)

                grammar.addrule(rulename, t.text)

            if t.pos_ == 'NOUN':
                rulename = f'NOUN'
                grammar.addrule(rulename, t.text)

            if t.pos_ == 'PRON':
                rulename = f'PRON'
                morph = t.morph
                prontype = ''.join(morph.get('PronType'))
                rulename = f'PRON_{prontype}'
                grammar.addrule(rulename, t.text)


class StoryGenerator:
    """Class to generate stories based on a grammar"""

    def generategrammar(self, filename='default.txt'):
        self.grammar.autopopulate(filename)

    def __init__(self, title='myStory'):
        self.title = title
        self.entrypoint = "nothing"  # rule to use as story start
        self.story = ""

    def __str__(self):
        return f"{self.title}:\n{self.story}\n"

    def entrypointrule(self, rulename):
        rulename = f'{rulename.upper()}'

        if self.grammar.isrule(rulename):
            self.entrypoint = rulename
            return True
        else:
            print(f'Error: rule {rulename} does not exist in grammar.')
            return False

    def generate(self):
        """
        Generate story from defined grammar. It starts by entrypointrule.

        :return:
        """
        if self.entrypoint == "nothing":
            print('Error: you need to establish an entrypoint first')
            return False

        print("Generating story...")
        self.story = self.grammar.expand(self.entrypoint)

    def reset(self):
        self.grammar.clear()

    def addrule(self, rulename, rulecontent):
        """
        Add a rule to this story generator. Rules come with two inputs. Their name and their content. For instance:

        addrule('ADJECTIVES', {'easy, 'bold', 'assertive'})

        :param rulename:
        :param rulecontent:
        :return:
        """
        self.grammar.addrule(rulename, rulecontent)

    grammar = StoryGrammar()

if __name__ == "__main__":
    print("This is a module and it is not to be used directly. Just use it properly...")