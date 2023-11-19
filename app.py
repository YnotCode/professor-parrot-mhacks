from flask import Flask
from flask import request, send_file, render_template, redirect

from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.chains import SimpleSequentialChain, LLMChain
from langchain.chat_models import ChatOpenAI
from openai import OpenAI

import redis
import bcrypt
import random
import os

import gdown
import os

if (not os.path.exists("data/apush")):
    gdown.download_folder(url="https://drive.google.com/drive/folders/1JHWn7R2B-YvaLO5SVOIG6r4Tkr05QOkU", output="data/apush")

if (not os.path.exists("data/bio")):
    gdown.download_folder(url="https://drive.google.com/drive/folders/1xooiUZIcY3GFZlTSNq8ReyJNRLc1d2gG", output="data/bio")

import json

app = Flask(__name__)
r = redis.Redis(host='redis-18020.c238.us-central1-2.gce.cloud.redislabs.com', port='18020', password=os.getenv("REDIS_KEY"), decode_responses=True)

r.set("avarkey@umich.edu-apushpage", 45)

from PyPDF2 import PdfReader

def generate_session_key():
    stringed = ""
    for x in range(10):
        num = random.randint(0, 9)
        stringed += str(num)
    return stringed

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/")
def hello_world():
    return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/authenticatesignup", methods=["POST"])
def authenticatesignup():
    data = {
        "name": request.form.get("name"),
        "pwd": request.form.get("pwd"),
        "email": request.form.get("email"),
        "learning-rate": 10,
    }

    if (r.sismember("users", data["email"])):
        return redirect("/signup?failedexists=true")

    r.sadd("users", data["email"])
    bytes = data["pwd"].encode('utf-8') 
    # generating the salt 
    salt = bcrypt.gensalt() 
    # Hashing the password 
    hash = bcrypt.hashpw(bytes, salt) 
    r.set(data["email"] + "-pwd", hash)
    r.set(data["email"] + "-name", data["name"])
    r.set(data["email"] + "-lrate", data["learning-rate"])
    r.set(data["email"] + "-apushpage", 21)
    r.set(data["email"] + "-biopage", 17)
    key = generate_session_key()
    r.set("key-" + key, data["email"])

    response = redirect("/")
    response.set_cookie("session-key", key)
    response.set_cookie("logged-in", "true")

    return response

@app.route("/getuserdata", methods=["GET", "POST"])
def getuserdata():
    if (request.method == "GET"):
        return "Blah"
    key = request.json.get("key")
    if (not key):
        print("h")
        return {"res": "failed"}

    email = r.get("key-" + key)
    if (not email):
        return {"res": "failed"}
    
    name = r.get(email + "-name")
    lrate = r.get(email + "-lrate")
    return {"res": "success", "name": name, "lrate": lrate}

@app.route("/getuserpage", methods=["GET", "POST"])
def getuserpage():
    if (request.method == "GET"):
        return "Blah"
    key = request.json.get("key")
    userclass = request.json.get("class")
    if (not key):
        print("h")
        return {"res": "failed"}
    if not userclass:
        print("F")
        return {"res": "failed"}

    email = r.get("key-" + key)
    if (not email):
        return {"res": "failed"}
    
    name = r.get(email + "-name")
    lrate = r.get(email + "-" + userclass + "page")
    return {"res": "success", "page": lrate}




@app.route("/authenticatelogin", methods=["POST"])
def authenticatelogin():
    data = {
        "email": request.form.get("email"),
        "pwd": request.form.get("pwd"),
    }
    if (not r.sismember("users", data["email"])):
        return redirect("/login?failedexists=true")
    
    
    # Taking user entered password  
    userPassword = data["pwd"]
    
    # encoding user password 
    userBytes = userPassword.encode('utf-8') 

    hash = r.get(data["email"] + "-pwd")
    hash = hash.encode("utf-8")
    
    # checking password 
    result = bcrypt.checkpw(userBytes, hash) 
    
    if result:
        key = generate_session_key()
        r.set("key-" + key, data["email"])

        response = redirect("/")
        response.set_cookie("session-key", key)
        response.set_cookie("logged-in", "true")
        return response
    
    return redirect("/login?failedpwd=true")


def get_page_text(filename, page):

    # creating a pdf reader object 
    reader = PdfReader('./data/' + filename)  
    
    # getting a specific page from the pdf file 
    page = reader.pages[page] 
    
    # extracting text from page 
    text = page.extract_text() 
    return text

def format_page(text):
    print("Formatting...")
    model = ChatOpenAI(model_name="gpt-3.5-turbo-1106", openai_api_key=os.getenv("OPENAI_KEY")) 
    
    template_initial = PromptTemplate.from_template("""Passage: {passage} 
    \nFormat the passage above so it looks like a texbook passage. Break the text into paragraphs and add blank lines between the paragraphs. Correct all formatting issues.""",)
    chain_initial = LLMChain(prompt=template_initial, llm=model)
    
    template_remove_initial = PromptTemplate.from_template("""Passage: {formattedagain}\nFormat the mardown above so that page number lines are removed and sections about figures are also removed. Output the final result in Markdown. """,)
    
    chain_remove_initial = LLMChain(prompt=template_remove_initial, llm=model)

    template_removing = PromptTemplate.from_template("""Passage: {formattedagain3}\nRemove any references to images from the passage above. Remove any reference to the source of the text as well. Also remove any learning objectives. Also remove any practice problems or questions. Output the final result in Markdown. """)
    
    chain_removing = LLMChain(prompt=template_removing, llm=model)
    
    

    template_bolding = PromptTemplate.from_template("""Passage: {formatted}\nFormat the mardown above so all the headers of sections are bolded. Make sure there is a blank line between the header and the content. Output the final result in Markdown. """,)
    
    chain_bolding = LLMChain(prompt=template_bolding, llm=model)

    sequential = SimpleSequentialChain(chains=[chain_initial])

    
    res = sequential.run(text)

    print("Finished Sequential")

    return res

def generate_pagecheck(text):
    model = ChatOpenAI(model_name="gpt-3.5-turbo-1106", openai_api_key=os.getenv("OPENAI_KEY"))
    question_template = PromptTemplate.from_template("""Passage: {passage} 
    \nGenerate a multiple choice question to test comprehension of the passage. Create the question and 4 answer choices marked A-D separated by blank lines. The last character should be the correct answer letter by itself with no other mention of the answer.""",)
    chain = LLMChain(prompt=question_template, llm=model)
    return chain.run(text)

@app.route("/getpagedata", methods=["GET"])
def getpagedata():
    
    number = request.args.get('page')
    
    userclass = request.args.get("class")
    
    approved = set()
    approved.add("apush")
    approved.add("bio")


    if not number or not userclass or userclass not in approved:
        return {"res": "failedhere"}
    
    exists = r.exists(userclass + "-gptpage" + number)
    if not exists:
        for file in os.listdir("./static/" + userclass):
            if ("gptpage" + str(number) + ".md" == file):
                exists = True
                f = open("static/" + userclass + "/gptpage" + str(number) + ".md", "r")
                r.set(userclass + "-gptpage" + number, f.read())
    if not exists:
        text = get_page_text(userclass + "/open.pdf", int(number))
        text = text.replace("\n", " ")
        gptd = format_page(text)
        r.set(userclass + "-gptpage" + number, gptd)
        return {"res": "success", "content": gptd}
    else:
        f = r.get(userclass + "-gptpage" + number)
        return {"res": "success", "content": f}
    #static/apush/gptpage" + str(number) + ".md"
    
@app.route("/generatequestion", methods=["GET"])
def getquestion():
    userclass = request.args.get('class')
    page = request.args.get('page')
    if not userclass or not page:
        return {"res": "failure"}

    f = r.get(userclass + "-gptpage" + page)
    content = f
    question = generate_pagecheck(content)
    return {"res": "success", "result": question}

@app.route("/increaseLearningRate", methods=["GET"])
def buffLearningRate():
    key = request.args.get('key')
    if not key:
        print("F")
        return {"res": "failure"}
    
    user = r.get("key-" + key)
    if not user:
        print("FF")
        return {"res": "failure"}
    
    lr = r.get(user + "-lrate")
    lr = int(lr) + 1
    if (lr > 10):
        lr = 10
    print("NEW LR", lr)
    r.set(user + "-lrate", lr)
    return {"res": "success"}

@app.route("/decreaseLearningRate", methods=["GET"])
def nerfLearningRate():
    key = request.args.get('key')
    if not key:
        print("F")
        return {"res": "failure"}
    
    user = r.get("key-" + key)
    if not user:
        print("FF")
        return {"res": "failure"}
    
    lr = r.get(user + "-lrate")
    lr = int(lr) - 1
    if (lr < 1):
        lr = 1
    print("NEW LR", lr)
    r.set(user + "-lrate", lr)
    return {"res": "success"}

@app.route("/advancePage", methods=["GET"])
def advancePage():
    key = request.args.get('key')
    userclass = request.args.get("class")
    if not key or not userclass:
        return {"res": "failure"}
    user = r.get("key-" + key)
    if not user:
        return {"res": "failure"}
    
    page = int(r.get(user + "-" + userclass + "page"))
    page += 1
    r.set(user + "-" + userclass + "page", page)
    return {"res": "success"}

@app.route("/getcourselength", methods=["GET"])
def getcourselength():
    userclass = request.args.get("class")
    if not userclass:
        return {"res": "failure"}
    classlength = int(r.get("class-" + userclass + "-length"))
    return {"res": "success", "length": classlength}

def generate_suggestion(text, lrate):
    model = ChatOpenAI(model_name="gpt-3.5-turbo-1106", openai_api_key=os.getenv("OPENAI_KEY"))
    suggest_template = PromptTemplate.from_template("""Passage: {passage}\nSkill level: {lrate}/10 
    \nGenerate an insightful footnote for the paragraph. Be brief (1 sentence). The complexity of each note should match the skill level given. Footnotes should expand on the passage and should not repeat information from the passage. Output only the footnote. """,)
    chain = LLMChain(prompt=suggest_template, llm=model)
    suggestion = chain.run({"passage": text, "lrate": lrate})
    return suggestion

@app.route("/classifywithkco", methods=["POST"])
def classifywithkco():
    passage = request.json.get("passage")
    page = request.json.get("page")
    userclass = request.json.get("class")
    approved = set()
    approved.add("apush")
    approved.add("bio")
    if not passage or not page or not userclass or userclass not in approved:
        return {"res": "failure"}
    
    print("FFFF", page)

    exists = r.exists("kco-" + page)
    if (exists):
        return {"res": "success", "result": r.get(userclass + "-kco-" + page)}
    

    big_template = PromptTemplate.from_template("""Key Concept Outline: {massive_text}\nPassage: {passage}\nUse the Key Concept Outline to classify the passage as one of the key concepts. Output only the label and definition of the key concept selected (i.e. 1.1.I.A- The spread of maize cultivation from present-day Mexico northward into the
present-day American Southwest and beyond supported economic development,
settlement, advanced irrigation, and social diversification among societies.)""")
    model = ChatOpenAI(model_name="gpt-4-1106-preview", openai_api_key=os.getenv("OPENAI_KEY"))
    chain = LLMChain(prompt=big_template, llm=model)

    kco_text = ""

    pagelengths = {
        "apush": (2, 27),
        "bio": (13, 16)
    }

    for i in range(pagelengths[userclass][0], pagelengths[userclass][1]):
        kco_text += get_page_text(userclass + "/keyconceptoutline.pdf", i)

    ans = chain.run({"massive_text": kco_text, "passage": passage})
    r.set(userclass + "-kco-" + page, ans)
    return {"res": "success", "result": ans}


@app.route("/aisuggestion", methods=["POST"])
def aisuggestion():
    passage = request.json.get("passage")
    lrate = request.json.get("lrate")

    if not passage or not lrate:
        print("FAILED")
        print("Failed parrot power")
        return {"res": "failure"}
    
    suggestion = generate_suggestion(passage, lrate)
    return {"res": "success", "tip": suggestion}

@app.route("/deleteAccount", methods=["GET"])
def deleteAccount():
    key = request.args.get("key")
    if not key:
        return {"res": "failure"}
    user = r.get("key-" + key)
    if not user:
        return {"res": "failure"}
    r.srem("users", user)
    
    
    return {"res": "success"}


# STEP 1 
# import libraries 
import fitz 
import io 
from PIL import Image
import base64
import requests

@app.route("/getimages", methods=["GET"])
def getimages():
    userclass = request.args.get("class")
    page_index = request.args.get("page")
    if not page_index or not userclass:
        return {"res": "failure"}
    
    #Define path to PDF file
    file_path = 'data/' + userclass + "/open.pdf"

    #Define path for saved images
    images_path = './'

    #Open PDF file
    pdf_file = fitz.open(file_path)

    #Create empty list to store images information
    images_list = []

    #Extract all images information from each page
    page_content = pdf_file[int(page_index)]
    images_list.extend(page_content.get_images())

    #Raise error if PDF has no images
    if len(images_list)==0:
        return {"res": "success", "images": [], "captions": []}


    final_list = []
    captions = []

    #Save all the extracted images
    for i, img in enumerate(images_list, start=1):
        #Extract the image object number
        xref = img[0]
        #Extract image
        base_image = pdf_file.extract_image(xref)
        #Store image bytes
        image_bytes = base_image['image']
        res = base64.b64encode(image_bytes).decode("utf-8")
        final_list.append(res)

    # OpenAI API Key
    api_key = os.getenv("OPENAI_KEY")

    # Getting the base64 string
    for n in final_list:
        base64_image = n

        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
        }

        payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": "Provide additional context about the image. Limit the answer to 1 brief sentence."
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
                }
            ]
            }
        ],
        "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        try:
            captions.append(response.json()["choices"][0]["message"]["content"])
        except:
            pass
    print(captions)
    return {"res": "success", "images": final_list, "captions": captions}

@app.route("/frqgenerate", methods=["GET", "POST"])
def frqgenerate():
    last_page = request.args.get("page")
    userclass = request.args.get("class")
    if not last_page:
        return {"res": "failed"}
    first_page = int(last_page) - 5
    selected_page = random.randrange(first_page, first_page + 5)
    frq_template = PromptTemplate.from_template("""“Distance and inadequate training in agricultural pursuits closed the frontier to eastern workingmen; instead  America was settled by successive waves of farmers who were already skilled in wresting a living from the  soil. Farming, even before the day of mechanization, was a highly technical profession; frontiering required a  knowledge of even more specialized techniques. Clearing the land, building a home, fencing fields, solving  the problem of defense, and planting crops on virgin soil all demanded experience few workingmen could  boast. . . .  “. . . Romantic characters took part [in frontier migration]: . . . trappers and leatherclad ‘Mountain Men,’  starry-eyed prospectors and hard-riding cowboys, badmen and vigilantes. But the true hero of the tale was the  hard-working farmer who, ax in hand, marched ever westward until the boundaries of his nation touched the  Pacific.”  Ray Allen Billington,   historian,   Westward   Expansion:   A   History   of   the  American   Frontier,   1949  “The rapid expansion of wagework in the United States . . . and the most intensive phase of the exploitation  and settlement of the western third of the continent were roughly contemporaneous processes that occurred  during   a   seventy-year   interval   [beginning   in   1848]. Y  et,   at   first   glance,   the   terms   frontier   and   wagework   seem  to describe mutually exclusive conditions. . . . In actuality, . . . one such conjunction [of these terms] was the  wageworkers’ frontier. . . .  “. . . The wageworkers’ frontier . . . was foremost a predominantly male community of manual labor  dependent upon others for wages in the extractive industries of the sparsely settled Rocky Mountain and  Pacific regions of the United States. . . . It also represented a zone of extremely rapid transition from  wilderness to industrial, post-frontier society. . . . The wageworkers’ frontier was a fragile entity forever at the  mercy of the outside world’s pricing of its basic [export] commodities. . . . All [commodities] were shippedout of the west because the Rocky Mountain and Pacific regions contained too few people . . . to constitute a  viable home market. Settlements on the wageworkers’ frontier tended to resemble factory towns in  Pennsylvania or Massachusetts.”  Carlos A. Schwantes, historian, “The Concept of the W  ageworkers’ Frontier,”  1987  
Using the quotations above as inspiration, generate a new quote relevant to the passage below. 
Passage: {passage}""")
    model = ChatOpenAI(model_name="gpt-3.5-turbo-1106", openai_api_key=os.getenv("OPENAI_KEY")) 
    chain = LLMChain(prompt=frq_template, llm=model)
    synthetic_passage = chain.run(get_page_text("/static/" + userclass + "/gptpage" + selected_page + ".md"))
    question_template = PromptTemplate.from_template("""Quote: {quote}\nGenerate an open-ended question that challenges a student's historical knowledge about the context of the quote. """)
    chain2 =  LLMChain(prompt=question_template, llm=model)
    actual_question = chain2.run(synthetic_passage)
    return {"res": "success", "passage_gen": synthetic_passage, 'question': actual_question}

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/learn")
def learn():
    return render_template("learn.html")

if __name__ == "__main__":
    app.run()
