from pythonforandroid.recipe import PythonRecipe


class SaiyanQuestRecipe(PythonRecipe):
    version = 'development'
    url = 'https://github.com/SaiyanQuest/SaiyanQuest/archive/development.zip'
    depends = ['setuptools']
    site_packages_name = 'saiyanquest'
    call_hostpython_via_targetpython = False
    install_in_hostpython = True

recipe = SaiyanQuestRecipe()
