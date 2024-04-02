import spacy
from spacy.training.example import Example
import random

nlp = spacy.load("en_core_web_sm")  
ner = nlp.get_pipe("ner")

# Add labels
ner.add_label("TECH")


train_data = [
    ("Looking for a skilled Java developer with expertise in Spring and Hibernate frameworks.", {"entities": [(22, 26, "TECH"), (55, 61, "TECH"), (66, 75, "TECH")]}),
    ("We need a Front-end Developer proficient in React.js, HTML, and CSS.", {"entities": [(44, 52, "TECH"), (54, 58, "TECH"), (64, 67, "TECH")]}),
    ("Hiring a Full-stack developer with experience in Node.js, Express.js, MongoDB, and Angular.", {"entities": [(49, 56, "TECH"), (58, 68, "TECH"), (70, 77, "TECH"), (83, 90, "TECH")]}),
    ("Looking for a Python Developer with Django and Flask experience.", {"entities": [(14, 20, "TECH"), (36, 42, "TECH"), (47, 52, "TECH")]}),
    ("Seeking a proficient C++ developer familiar with Qt and Boost libraries.", {"entities": [(21, 24, "TECH"), (49, 51, "TECH"), (56, 61, "TECH")]}),
    ("Hiring a .NET developer with experience in C# and ASP.NET.", {"entities": [(9, 13, "TECH"), (43, 45, "TECH"), (50, 57, "TECH")]}),
    ("In search of a developer skilled in Ruby and Rails for web development projects.", {"entities": [(36, 40, "TECH"), (45, 50, "TECH")]}),
    ("We require an expert in cloud computing, familiar with AWS and Azure services.", {"entities": [(55, 58, "TECH"), (63, 68, "TECH")]}),
    ("Database Administrator with experience in SQL, Oracle, and Microsoft SQL Server.", {"entities": [(42, 45, "TECH"), (47, 53, "TECH"), (59, 79, "TECH")]}),
    ("Mobile developer proficient in Swift, Kotlin, and React Native for iOS and Android development.", {"entities": [(31, 36, "TECH"), (38, 44, "TECH"), (50, 62, "TECH")]}),
    ("Experienced data scientist with proficiency in R, Python, and TensorFlow.", {"entities": [(47, 48, "TECH"), (50, 56, "TECH"), (62, 72, "TECH")]}),
    ("Seeking software engineer with expertise in Go and Docker for backend systems.", {"entities": [(44, 46, "TECH"), (51, 57, "TECH")]}),
    ("Looking for a developer with experience in PHP and Laravel framework.", {"entities": [(43, 46, "TECH"), (51, 58, "TECH")]}),
    ("Hiring for a position that requires knowledge in Salesforce and Apex programming.", {"entities": [(49, 59, "TECH"), (64, 68, "TECH")]}),
    ("Need a developer familiar with JavaScript, TypeScript, and Vue.js for front-end development.", {"entities": [(31, 41, "TECH"), (43, 53, "TECH"), (59, 65, "TECH")]}),
    ("Senior DevOps engineer with experience in Jenkins, Docker, and Kubernetes.", {"entities": [(42, 49, "TECH"), (51, 57, "TECH"), (63, 73, "TECH")]}),
    ("Backend Developer experienced with Python, Flask, and PostgreSQL needed.", {"entities": [(35, 41, "TECH"), (43, 48, "TECH"), (54, 64, "TECH")]}),
    ("Front-end specialist with deep knowledge in React and Redux.", {"entities": [(44, 49, "TECH"), (54, 59, "TECH")]}),
    ("The candidate should be proficient in Adobe Photoshop and Illustrator for graphic design.", {"entities": [(44, 53, "TECH"), (58, 69, "TECH")]}),
    ("Java developer with experience in Spring Boot and Microservices architecture.", {"entities": [(0, 4, "TECH"), (34, 45, "TECH"), (50, 63, "TECH")]}),
    ("Seeking a Data Scientist proficient in Python, R, and machine learning libraries like TensorFlow and PyTorch.", {"entities": [(39, 45, "TECH"), (47, 48, "TECH"), (54, 70, "TECH"), (86, 96, "TECH"), (101, 108, "TECH")]}),
    ("Mobile Application Developer with proficiency in Swift and Objective-C.", {"entities": [(49, 54, "TECH"), (59, 69, "TECH")]}),
    ("Web Developer with proficiency in HTML, CSS, JavaScript and experience with Angular and React.", {"entities": [(34, 38, "TECH"), (40, 43, "TECH"), (45, 55, "TECH"), (76, 83, "TECH"), (88, 93, "TECH")]}),
    ("Cloud Engineer experienced in AWS, Google Cloud Platform, and Azure.", {"entities": [(30, 33, "TECH"), (35, 47, "TECH"), (62, 67, "TECH")]}),
    ("Seeking an expert in database technologies like MySQL, MongoDB, and Oracle.", {"entities": [(48, 53, "TECH"), (55, 62, "TECH"), (68, 74, "TECH")]}),
    ("Experienced system administrator knowledgeable in Linux, Windows Server, and networking.", {"entities": [(50, 55, "TECH"), (57, 71, "TECH"), (77, 87, "TECH")]}),

]

# Train NER
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.begin_training()

    for itn in range(20): 
        print(f"Starting iteration {itn}")
        random.shuffle(train_data)
        losses = {}

        # Batch the examples and iterate over them
        for batch in spacy.util.minibatch(train_data, size=2):  
            examples = [Example.from_dict(nlp.make_doc(text), annotations) for text, annotations in batch]
            nlp.update(examples, drop=0.5, losses=losses)  

        print(losses)

# Save model to disk
nlp.to_disk("model_upgrade")
