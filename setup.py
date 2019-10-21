#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: setup.py 11516 2019-05-02 18:05:42Z Lavender $
#
# Copyright (c) 2017 Nuwa Information Co., Ltd, All Rights Reserved.
#
# Licensed under the Proprietary License,
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at our web site.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# $Author: Lavender $
# $Date: 2019-05-03 03:05:42 +0900 (週五, 03 五月 2019) $
# $Revision: 11516 $

import os
import sys
import time
import logging
import shutil
import json
import argparse
import locale
import traceback

try:
    import colorama 
except Exception as e:
    os.system("pip install colorama==0.4.1")
    import colorama
    
colorama.init()

try:
    from termcolor import colored, cprint
except Exception as e:
    os.system("pip install termcolor==1.1.0")
    from termcolor import colored, cprint

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)
SETUP_DIR = os.path.dirname(os.path.abspath(__file__))
CKEDITOR_SETTINGS = \
'''
CKEDITOR_SETTINGS = {
    'language': '',
    'toolbar_CMS': [
        ['cmsplugins',],
       
        ['Source', '-', 'Save', 'NewPage', 'DocProps', 'Preview',
         'Print', '-', ' Templates'],
        ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-',
         'Undo', 'Redo'],
        ['Find', 'Replace', '-', 'SelectAll', '-', 'SpellChecker',
         'Scayt'],
        ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select',
        'Button', 'ImageButton', 'HiddenField'],
        ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript',
        'Superscript', '-', 'RemoveFormat'],
        ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-',
        'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter',
        'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl'],
        ['Link', 'Unlink', 'Anchor'],
        ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley',
        'SpecialChar', 'PageBreak', 'Iframe'],
        ['Styles', 'Format', 'Font', 'FontSize'],
        ['TextColor', 'BGColor'],
        ['Maximize', 'ShowBlocks', '-', 'About'],
    ],
    'skin': 'moono-lisa',
}
'''

if sys.version_info >= (3, 7):
    logger.info(colored(
        "Python 3.7 not supported yet, please use 3.6 or below.", "yellow"))
    sys.exit(1)

def copyToPath(baseDir, templateDir, staticDir, mode):
    if not templateDir:
        templateDir = os.path.join(baseDir, 'templates')
    if not staticDir:
        staticDir = os.path.join(baseDir,'static')
       
    logger.info(colored("-----Start copy templates-----", "yellow"))
    if not os.path.exists(staticDir):
        os.mkdir(staticDir)
    if not os.path.exists(templateDir):
        os.mkdir(templateDir)
    for root, dirs, files in os.walk(os.path.join(SETUP_DIR, "static")):
        for d in dirs:
            index = os.path.join(root, d).index("static") + len("static/")
            path = os.path.join(
                staticDir, os.path.join(os.path.join(root, d))[index:])
            if not os.path.exists(path):
                os.mkdir(path)
               
    if not os.path.exists(os.path.join(baseDir, "fixtures")):
        os.mkdir(os.path.join(baseDir, "fixtures"))
   
    for root, dirs, files in os.walk(SETUP_DIR):
        for f in files:
            if f == 'setup.py':
                continue
            origin = os.path.join(root, f)
           
            if os.path.join(SETUP_DIR, "static") in root:
                index = len(os.path.join(SETUP_DIR, "static")) + 1
                dst = os.path.join(staticDir, origin[index:])
            elif os.path.join(SETUP_DIR, "templates") in root:
                dst = os.path.join(templateDir, f)
            elif os.path.join(SETUP_DIR, "fixtures") in root:
                index = len(os.path.join(SETUP_DIR, "fixtures")) + 1
                dst = os.path.join(baseDir, "fixtures", origin[index:])
            else:
                continue
           
            if os.path.isfile(dst):
                logger.error(
                    colored("%s exists. failed to copy file." % dst, "red"))
            else:
                shutil.copyfile(origin, dst)
                logger.info("Succeed to copy file to %s." % dst)
   
def findSettings(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            if f == 'settings.py':
                return os.path.join(root, f)
    return None
   
def canAddPlugin(pkgName, pluginName):
    result = 0
   
    try:
        __import__(pluginName)
    except Exception as e:
        result = os.system("pip install %s" % pkgName)
       
    if result != 0:
        return False
    else:
        return True
               
def writeSettings(settingsPath, templateDir, staticDir, hasCmsTemplate, baseDir,
                  wizard=False, createProject=False):
    logger.info(
        colored("-----Start write and backup settings.py-----", "yellow"))
    def getCMSTemplates():
        templates = []
       
        path = os.path.join(SETUP_DIR, 'templates')
        index = None
               
        for template in os.listdir(path):
            if "_tracking" in template:
                continue
            if template.lower() == 'index.html':
                index = template
                continue
            templates.append((template, template))
       
        if index:
            return [(index, index),] + templates
        else:
            return templates
   
    settingsDir = os.path.dirname(settingsPath)
    bak = os.path.join(settingsDir, 'settings.py.bak')
    if os.path.isfile(bak):
        logger.error(colored("%s exists. failed to backup file." % bak, "red"))
        return 
    shutil.copyfile(settingsPath, bak)
    logger.info(colored("Succeed to backup settings.py to %s." % bak, "yellow"))
               
    with open(settingsPath, 'r') as settings:
        content = settings.read()
               
    with open(settingsPath, 'w') as settings:   
        if hasCmsTemplate:
            content += \
'''
CMS_TEMPLATES = list(CMS_TEMPLATES)
CMS_TEMPLATES += %s
''' % str(getCMSTemplates())
        else:
            content += \
'''
CMS_TEMPLATES = %s
''' % str(getCMSTemplates())
        if not templateDir:
            content = content.replace(
                "'DIRS': []", "'DIRS': [os.path.join(BASE_DIR, 'templates'),]")
           
        if not staticDir:
            content += \
'''
if DEBUG:
    STATICFILES_DIRS = (
        os.path.join(BASE_DIR, 'static'),
    )
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
'''
        import cms
    
        if cms.__version__.startswith('3.5'):
            pluginList = []
            requirementList = []
        else:
            pluginList = []
            requirementList = []
        
        if createProject:
            if wizard:
                if sys.version_info.major == 3:
                    yesOrNo = input(
                        "Do you want to install djangocms_history and "
                        "all ckeditor features?[yes/no]")
                else:
                    yesOrNo = raw_input(
                        "Do you want to install djangocms_history and "
                        "all ckeditor features?[yes/no]")
            else:
                yesOrNo = 'yes'
                
            if yesOrNo == 'yes':
                if cms.__version__.startswith('3.4'):
                    if canAddPlugin(
                        'djangocms-file', 'djangocms_file==2.0.2'):
                        pluginList.append('djangocms_file')
                        requirementList.append('djangocms_file==2.0.2')
                        
                    if canAddPlugin(
                        'djangocms-picture', 'djangocms_picture==2.0.6'):
                        pluginList.append('djangocms_picture')
                        requirementList.append('djangocms_picture==2.0.6')
                        
                if canAddPlugin(
                    'djangocms-history', 'djangocms_history==0.5.3'):
                    pluginList.append('djangocms_history')
                    requirementList.append('djangocms_history==0.5.3')
                if canAddPlugin(
                    'djangocms-forms', 'djangocms_forms==0.2.5'):
                    pluginList.append('djangocms_forms')
                    requirementList.append('djangocms_forms==0.2.5')
                    
            requirementList.append('djangocms_text_ckeditor==3.5.3')
            
            with open(os.path.join(baseDir, "requirements.txt"), 'a') as reqs:
                reqs.write("\n")
                for r in requirementList:
                    reqs.write("%s\n" % r)
                   
        content += "INSTALLED_APPS += %s" % str(tuple(pluginList))
        content += CKEDITOR_SETTINGS
        settings.write(content)
           
               
    logger.info(colored("Succeed to write settings.py", "yellow"))
               
def loadData(baseDir, language):
    logger.info(colored("-----Start load data-----", "yellow"))
    data = os.path.join(".", 'fixtures', 'initial_data.json')
    result = os.system("%s manage.py migrate" % sys.executable)
    if not result == 0:
        logger.error(colored("Can not migrate db.", "red"))
        return False
       
    result = os.system("%s manage.py loaddata \"%s\"" % (sys.executable, data))
   
    if not result == 0:
        logger.error(colored("Can not loaddata.", "red"))
        return False
   
    from cms.models.pagemodel import Page
    from cms.models.titlemodels import Title
    from cms.models.pluginmodel import CMSPlugin
    from django.db import transaction
   
    @transaction.atomic
    def modifyData():
        for plugin in CMSPlugin.objects.all():
            plugin.language = language
            plugin.save()
        for page in Page.objects.all():
            page.languages = language
            page.save()
        for title in Title.objects.all():
            title.language = language
            title.save()
    modifyData()
       
    return True
       
if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Path to Project')
        parser.add_argument(
            "path", metavar='path', 
            type=str,  nargs='?', default=".",
            help="Path to project, default is '.'"
        )
           
        parser.add_argument(
            '-w', '--wizard', 
            action='store_true',
            help="Run the configuration wizard")   
       
        args = parser.parse_args()
       
        wizard = args.wizard
        mode = 'user'
        
        local = locale.getdefaultlocale()
        if len(local) == 2 and local[0]:
            local = local[0]
        
        if os.path.isfile(os.path.join(SETUP_DIR, 'MANIFAST.INFO')):
            with open(os.path.join(SETUP_DIR, 'MANIFAST.INFO')) as f:
                data = json.loads(f.read())
                
            cmsVersion = data["DjangoCMSVersion"]
        else:
            cmsVersion = '3.5.1'
        
        if cmsVersion.startswith("3.4"):
            installVersion = "0.9.7"
        elif cmsVersion.startswith("3.5"):
            installVersion = "1.0.0"
        elif cmsVersion.startswith("3.6"):
            installVersion = "1.1.0"
        else:
            installVersion = "1.1.0"
           
        path = args.path
       
        settingsPath = findSettings(path)
        
        createProject = False
       
        if not settingsPath:
            if sys.version_info.major == 3:
                print()
                projectName = input(
                    ("Django project not found. "
                     "Auto create one by djangocms-installer==%s."
                     "\nPlease input a project name:") % installVersion)
            else:
                print
                projectName = raw_input(
                    ("Django project not found. "
                     "Auto create one by djangocms-installer==%s."
                     "\nPlease input a project name:") % installVersion)
            
            result = os.system(
                "pip install djangocms-installer==%s" % installVersion)
            
            if result != 0:
                logger.error(colored(
                    "Unable to run pip, please check your pip configuration, "
                    "maybe it is because you didn't set python in system PATH "
                    "or broken network connection.", "red"))
                sys.exit(1)
           
            path = os.path.join(path, projectName)
           
            if wizard:
                command = "djangocms -f -p \"%s\" \"%s\" -w" % (
                    path, projectName)
            else:
                command = "djangocms -f -p \"%s\" \"%s\"" % (
                    path, projectName)
                    
            if local and local.upper() in ["ZH_TW", "ZH_HANT"]:
                command = "%s --languages=zh-hant" % command
                
            result = os.system(command)
           
            createProject = True
               
            if not result == 0:
                print("")
                logger.error(colored(
                    "Please check your environment "
                    "which djangocms-installer is installed or "
                    "upgrade to the latest.", "red"))
                sys.exit(1)
               
            settingsPath = findSettings(path)
        else:
            path = os.path.dirname(os.path.dirname(settingsPath))
       
        settingModule = os.path.splitext(settingsPath[len(path) + 1:])[0]
        settingModule = settingModule.replace("/", ".")
        settingModule = settingModule.replace("\\", ".")
       
        sys.path.append(path)
        os.environ['DJANGO_SETTINGS_MODULE'] = settingModule
       
        import django
       
        try:
            import cms
        except Exception as e:
            os.system("pip install django-cms==%s" % cmsVersion)
            import cms

        import cms
        
        if cms.__version__.startswith('3.5'):
            try:
                import cmsplugin_filer_image
            except Exception as e:
                os.system("pip install cmsplugin-filer==1.1.3")
                import cms
                
        import djangocms_text_ckeditor
        if not djangocms_text_ckeditor.__version__.startswith("3.5"):
            try:
                os.system("pip install -U djangocms_text_ckeditor==3.5.3")
            except Exception as e:
                logger.error(
                    colored("Can't install djangocms_text_ckeditor==3.5.3", 
                            "red"))
                sys.exit(1)
           
        cmsVersion = cms.__version__.split('.')
       
        cms34 = True
        try:
            if int(cmsVersion[0]) <= 3 and int(cmsVersion[1]) <= 4:
                cms34 = True
            else:
                cms34 = False
        except Exception as e:
            cms34 = False
           
        if cms34:
            if not (django.VERSION[0] == 1 and django.VERSION[1] <= 10):
                logger.error(colored(
                    "Your installed Django above 1.10 which is not supported by "
                    "Django CMS 3.4 yet, please reinstall Django or you may "
                    "encounter some issues while using Django CMS.", "red"))
                sys.exit(1)
        django.setup()
       
        from django.conf import settings
       
        baseDir = settings.BASE_DIR
       
        apps = [
            'cms',
            'menus',
            'sekizai',
            'treebeard',
            'djangocms_text_ckeditor',
            'filer',
            'easy_thumbnails',
        ]
       
        endSetup = False
        for app in apps:
            if not app in settings.INSTALLED_APPS:
                logger.error(
                    colored(
                    "The app doesn't be included in INSTALLED_APPS: %s" % 
                    app, "red"))
                endSetup = True
       
        if endSetup:
            print("")
            logger.error(
                colored("The project does not support django cms. "
                "Please follow the instructions at "
                "http://docs.django-cms.org/en/stable/how_to/install.html", 
                "red"))
            sys.exit(1)
               
        try:
            templateDir = settings.TEMPLATES[0]['DIRS'][0]
        except Exception as e:
            templateDir = None
       
        try:
            staticDir = settings.STATICFILES_DIRS[0]
        except Exception as e:
            staticDir = None
       
        copyToPath(baseDir, templateDir, staticDir, mode)
       
        if hasattr(settings, "CMS_TEMPLATES"):
            hasCmsTemplate = True
        else:
            hasCmsTemplate = False
           
        writeSettings(settingsPath, 
            templateDir, staticDir, hasCmsTemplate, baseDir,
            wizard=wizard, createProject=createProject)
           
        os.chdir(baseDir)
           
        success = loadData(baseDir, settings.LANGUAGE_CODE)
        if not success:
            print("")
            logger.error(
                colored("Please check the project's db was migrated.", "red"))
        else:
            attrs=['bold']
            print("")
            
            logger.info(
                colored(
                    "Get into ", "yellow") +
                colored("\"%s\"" % path, "white", attrs=['bold',]) +
                colored(" directory and type ", "yellow") +
                colored(
                    "\"python manage.py runserver\"", "white", 
                    attrs=['bold',]) +
                colored(" to start your project" , "yellow")
            )
                        
            if createProject:
                logger.info(
                    colored(
                        "Please enter ", "yellow") +
                    colored("http://localhost:8000/?edit", "white",  
                        attrs=['bold',]) +
                    colored(
                        " to show CMS toolbar. Default super user is ", 
                        "yellow") +
                    colored(
                        "'admin' password: 'admin'.", "white", attrs=['bold',])
                )
                
    except Exception as e:
        print("")
        logger.error(colored("ERROR MESSAGE:", "red"))
        traceback.print_exc()
        print("")
        logger.error(colored(
            "If you encounter \"django.db.utils.OperationalError: "
            "Problem installing fixtures: no such table: cms_page__old\" "
            "or \"sqlite3.OperationalError: no such table: "
            "cms_cmsplugin__old\", something with \"__old\", "
            "this caused by Django's issue. Please see link: ", "red"))
        logger.error(
            colored("https://github.com/django/django/pull/"
            "10733/commits/c8ffdbe514b55ff5c9a2b8cb8bbdf2d3978c188f", "yellow"))
        logger.error(
            colored("to modify your schema.py to fix this problem.", "red"))
    try:
        import json
        if os.path.isfile(os.path.join(SETUP_DIR, 'MANIFAST.INFO')):
            with open(os.path.join(SETUP_DIR, 'MANIFAST.INFO')) as f:
                data = json.loads(f.read())
            tid = 'UA-92158820-3'
            cid = data['upc']
            ec = "Product"
            ea = "Setup"
            el = "upc=%s" % data['upc']
            url = ("https://www.google-analytics.com/collect?"
                    "v=1&t=event&tid=%s&cid=%s&ec=%s&ea=%s&el=%s&ev=300" % (
                        tid, cid, ec, ea, el))
            if sys.version_info.major == 3:
                import urllib.request
                result = urllib.request.urlopen(url)
            else:
                import urllib2
                result = urllib2.urlopen(url)
    except Exception as e:
        pass