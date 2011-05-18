from distutils.core import setup

files = ["settings/*.conf.default"]

setup(name='Automaton',
      version='0.9',
      description='Automaton automation application',
      url="http://github.com/nemec",
      author='Daniel Nemec',
      author_email='djnemec@gmail.com',

      packages=['automaton',
                'automaton.plugins',
                'automaton.lib',
                'automaton.lib.automaton_thrift',
                'automaton.lib.automaton_thrift.python'],
      package_data = {'automaton': files},
      scripts = ['automaton_server']
     )

