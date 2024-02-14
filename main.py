import os
import glob
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
llm = ChatOpenAI()

FOLDER_NAME = 'crud-app-sequelize'
SPRING_FOLDER_NAME = FOLDER_NAME + '-spring-boot'
PATH = '../{}'.format(FOLDER_NAME)

def commentedCode():
# --------------------------------------------------------
# Get the folder structure of the original application

# def get_folder_structure(path: str):
#     folder_structure = ''
#     for root, dirs, files in os.walk(path):
#         level = root.replace(path, '').count(os.sep)
#         indent = ' ' * 4 * (level)
#         subindent = ' ' * 4 * (level + 1)
#         for file in files:
#             folder_structure += '{}{}'.format(subindent, file) + '\n'
#     return folder_structure

# folder_strucutre = get_folder_structure('../{}'.format(FOLDER_NAME))

# get_folder_structure_prompt  = ChatPromptTemplate.from_messages([
#     ("system", "You are a software engineer and you are working on a project to migrate a express application to a spring boot application. You need to read the original express folder strucuture and generate a new folder structure for the spring boot application with single one to one mapping of the files."),
#     ("user", "{input}")
# ])


# folder_structure_chain = get_folder_structure_prompt | llm
# new_folder_strucutre = folder_structure_chain.invoke({
#     "input": "I want to migrate the the following application named {} which has folder strucutre as : {} to a spring boot application named {} . The answer should strictly contain folder structure only without additional text, explanation or note".format(FOLDER_NAME, folder_strucutre, (FOLDER_NAME + '-spring-boot'))
# }).content

# print(new_folder_strucutre)
    return


# --------------------------------------------------------

print('Step 1. Creating the folder structure for the spring boot application..............')
folder_paths = [
    '{}/src/main/java/com/example/{}/config'.format(SPRING_FOLDER_NAME, SPRING_FOLDER_NAME),
    '{}/src/main/java/com/example/{}/controller'.format(SPRING_FOLDER_NAME, SPRING_FOLDER_NAME),
    '{}/src/main/java/com/example/{}/model'.format(SPRING_FOLDER_NAME, SPRING_FOLDER_NAME),
    '{}/src/main/java/com/example/{}/repository'.format(SPRING_FOLDER_NAME, SPRING_FOLDER_NAME),
    '{}/src/main/java/com/example/{}/service'.format(SPRING_FOLDER_NAME, SPRING_FOLDER_NAME),
]

for path in folder_paths:
    if not os.path.exists(path):
        os.makedirs(path)


file_paths = [
    '{}/src/main/resources/application.properties'.format(SPRING_FOLDER_NAME),
    '{}/pom.xml'.format(SPRING_FOLDER_NAME),
    '{}/.gitignore'.format(SPRING_FOLDER_NAME),
    '{}/README.md'.format(SPRING_FOLDER_NAME),
]

for file_path in file_paths:
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))


# --------------------------------------------------------
# Conversion of package.json to pom.xml

print('Step 2. Converting package.json to pom.xml..............')

def get_package_json(path: str):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file == 'package.json':
                with open(os.path.join(root, file), 'r') as f:
                    return f.read()
    return None


pox_ml_generator_prompt = ChatPromptTemplate.from_messages([
    ("system", '''You are a software engineer and you are working on a project to migrate a express application to a spring boot application. 
     You need to read the original express package.json and generate a new pom.xml for the spring boot application.
     Dont assume any dependencies, you need to convert the necessay dependencies from package.json to pom.xml
     The final output should just be the contents of the pom.xml file.'''),
    ("user", "{input}")
])

pox_xml_generator_chain = pox_ml_generator_prompt | llm
pom_xml_content = pox_xml_generator_chain.invoke({
    "input":'''I want to migrate the the following application named {} which has package.json as : {} to a spring boot application named {} . 
    The answer should strictly  contain pom.xml file content only without any additional text or information'''.format(FOLDER_NAME, get_package_json('../{}'.format(FOLDER_NAME)), (FOLDER_NAME + '-spring-boot'))
}).content


# print(pom_xml_content)


file = open('{}/pom.xml'.format(FOLDER_NAME + '-spring-boot'), 'w+')
file.write(pom_xml_content)
file.close()


# --------------------------------------------------------
# Writing the application.properties file using llm

print('Step 3. Writing the application.properties file..............')

application_properties_prompt = ChatPromptTemplate.from_messages([
    ("system", '''You are a software engineer and you are working on a project to migrate a express application to a spring boot application.
        You need to read the generate a new application.properties for the spring boot application.
        The final output should just be the contents of the application.properties file.'''),
        ("user", "{input}")
])

application_properties_chain = application_properties_prompt | llm

application_properties_content = application_properties_chain.invoke({
    "input": '''I want to migrate the the following application named {} to a spring boot application named {}. 
    Based on pom.xml content which is {} generate the neccesary application.properties file with correct and required properties key value pair.  
    The answer should strictly  contain application.properties file content only without any additional text or information '''.format(FOLDER_NAME, (FOLDER_NAME + '-spring-boot'), pom_xml_content)
}).content

file = open('{}/src/main/resources/application.properties'.format(FOLDER_NAME + '-spring-boot'), 'w+')
file.write(application_properties_content)
file.close()


# --------------------------------------------------------
# Iteratively going over the files in the original application (in src folder only and ts/js files only) and generating the corresponding files in the spring boot application

def get_files(path: str):
    print('Entering and looking for files in ...... {}'.format(path))
    Files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.ts') or file.endswith('.js'):
                Files.append(os.path.join(root, file))
    return Files

def get_file_content(file_path: str):
    with open(file_path, 'r') as f:
        return f.read()
    
def get_file_content_prompt(File_path: str):

    path_for_file_prompt = ChatPromptTemplate.from_messages([
        ("system", '''You are a software engineer and you are working on a project to migrate a express application to a spring boot application.
        You need to read the read the code , along with the given folder structure of spring boot application , generate path where that file should be located with correct file extension related to spring boot .
        The final output should just be the path file with correct file name and  extension following spring boot application'''),
        ("user", "{input}")
    ])
    path_for_file_chain = path_for_file_prompt | llm
    file_path = path_for_file_chain.invoke({
        "input": '''I want to migrate the the following file named {} to a spring boot application named {}. 
        The folder structure for spring application folder is {}. 
        The answer should strictly contain the path where the file with correct name and file extension  spring boot should be located in the spring boot application 
        without any additional text, info or heading as it will be directly feed to machine for creating and writing files.'''.format(File_path, (FOLDER_NAME + '-spring-boot'), ('{}'.format(folder_paths)))
    }).content

    print('Getting file content for file: ', file_path)

    file_content_prompt = ChatPromptTemplate.from_messages([
        ("system", '''You are an experience java and express developer and you are working on a project to migrate a express application to a spring boot application.
        You are converting one file at a time and generating the corresponding code file for the spring boot application.
        You need to read the original file content and generate a new file content for the spring boot application.
        The final output should just be the code snippet of the file without any additional info or explanation or heading on top or bottom of code snippet. 
        Just give the plain code with proper package name and imports as it will be directly feed to a machine and not a human.'''),
        ("user", "{input}")
    ])

    file_content_chain = file_content_prompt | llm
    file_content = file_content_chain.invoke({
        "input": '''I want to migrate the the following file named {} to a spring boot application named {}. 
        Based on the original file content which is {} and the pom.xml file {} generate the neccesary java code for implementing the same logic in spring boot.  
        The answer should strictly contain only code snippet along with correct package name without any additional info or explanation or heading on top or bottom of code snippet. 
        Use imports only using pom.xml and dont recommend any other dependencies except for those defined in the pom.xml file'''.format(file_path.split('/')[-1], (FOLDER_NAME + '-spring-boot'), get_file_content(File_path), pom_xml_content)
    }).content


    
    print(file_content,'/n', file_path)
    return file_content, file_path


print('Step 4. Collection for files started')

files = get_files('../{}'.format(FOLDER_NAME))

print('Step 5. Collection for files completed')
print('Files are: ', files)


for file in files:
    file_content, file_path = get_file_content_prompt(file)
    file = open(file_path, 'w+')
    file.write(file_content)
    file.close()


# --------------------------------------------------------
    