import json
import os
import shutil
from flask import Blueprint, request, render_template
from flask import current_app as app
from flask_cors import cross_origin
from app.models import db, Image, PredictedTags, ActualTags
from app.views.utils import (
    tag_mappings, 
    reverse_tag_mappings, 
    insert_db
)
from app.exceptions.Error import Error

colorizer = Blueprint("colorizer", __name__)

@colorizer.route("/")
@cross_origin()
def index():
    return "Welcome to the Manga Colorizer!"

@colorizer.route("/colorize", methods=["POST"])
@cross_origin()
def colorize():

    try:
        file = request.files["image"]
    except KeyError:
        raise Error(
            "Unprocessable_Entity",
            "Please include an 'image' key in your request.",
            422
        )

    original_name = file.filename

    # get image_serial of last inserted value so we can add 1 to name the new image
    image = Image.query.order_by(Image.id).all()

    if image:
        # extract the last image and add 1 to its serial # to get the next one's serial #
        last_inserted_img = image[-1]
        last_mono_id = os.path.splitext(last_inserted_img.image_serial)[0]
        image_serial = "{}.jpg".format(str(int(last_mono_id) + 1))
        image_id = last_inserted_img.id + 1
    else:
        # if image database is empty, name the first image 7100000
        image_serial = "7100000.jpg"
        image_id = 1

    # save the file
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], image_serial))

    """
    Model not yet integrated. 
    Get the new image back. 
    Save the new image in the right folder.
    Save the tags in the prediction databases.
    """
    # output of the model hard coded.
    shutil.copyfile(
        "src/img_storage/uploads/{}".format(image_serial), 
        "src/img_storage/model_predictions/{}".format(image_serial)
    )
    predicted_tags = [27, 31, 30]
    predicted_main_tag = 27

    # insert into image db
    new_image = Image(original_name=original_name, image_serial=image_serial, predicted_main_tag=predicted_main_tag)
    insert_db(new_image)

    # insert into predicted tags db
    for tag_number in predicted_tags:
        pt = PredictedTags(image_id=image_id, tag_name=tag_mappings.get(tag_number), tag_number=tag_number)
        insert_db(pt)

    colorized_img_and_tags = {
        "predicted_main_tag": predicted_main_tag,
        "predicted_tags": predicted_tags,
        "image_directory": image_serial,
        "id": image_id
    }

    return colorized_img_and_tags

@colorizer.route("/model-output", methods=["GET"])
@cross_origin()
def model_output():
    # make sure key is correct
    try:
        image_id = request.args["id"]
    except KeyError:
        raise Error(
            "Unprocessable_Entity",
            "Please include an 'id' key in your request.",
            422
        )

    # type checking
    if not isinstance(image_id, int):
        raise Error(
            "Wrong_Data_Type",
            "Please ensure your ID is an int.",
            422
        )

    image = Image.query.filter_by(id=image_id).first()

    # raise error if image isn't found in db
    if not image:
        raise Error(
            "Not_Found",
            "The image does not exist inside the database",
            404
        )

    predicted_tags_query = PredictedTags.query.filter_by(image_id=image_id).all()
    predicted_tags = [tags.tag_number for tags in predicted_tags_query]

    return {
        "image_serial": image.image_serial,
        "predicted_main_tag": image.predicted_main_tag,
        "predicted_tags": predicted_tags
    }

@colorizer.route("/correct-output/<id>", methods=["PATCH"])
@cross_origin()
def correct_output(id):
    # make sure json can be decoded
    try:
        tag_information = json.loads(request.data)
    except json.decoder.JSONDecodeError:
        raise Error(
            "Unprocessable_Entity",
            "Error decoding JSON.",
            422
        )

    # check if all required keys exist
    required_keys = ["actual_main_tag", "tags"]
    for key in required_keys:
        if key not in tag_information.keys():
            raise Error(
                "Unprocessable_Entity",
                "Please ensure key {} exists".format(key),
                422
            )

    actual_main_tags = tag_information["actual_main_tag"]
    tags = tag_information["tags"]
    
    # check if tag exists (implicit type checking)
    if not tag_mappings.get(actual_main_tags):
        raise Error(
            "Nonexistent_Tag",
            "Tag does not exist.",
            404
        )

    if not isinstance(tags, list):
        raise Error(
            "Wrong_Data_Type",
            "Ensure 'tags' is a list",
            422
        )
    
    for indiv_tag in tags:
        if not tag_mappings.get(indiv_tag):
            raise Error(
                "Nonexistent_Tag",
                "Tag does not exist.",
                404
            )
    
    # update the image with actual_main_tag
    image = Image.query.filter_by(id=id).first()

    if not image:
        raise Error(
            "Not_Found",
            "The image does not exist inside the database",
            404
        )

    image.actual_main_tag = actual_main_tags
    insert_db(image)

    # places values in actual_tags table
    for tag_number in tags:
        actual_tags = ActualTags(image_id=image.id, tag_name=tag_mappings.get(tag_number), tag_number=tag_number)
        insert_db(actual_tags)

    # copy the file from uploads to ground_truth
    shutil.copyfile(
        "src/img_storage/model_predictions/{}".format(image.image_serial), 
        "src/img_storage/ground_truth/{}".format(image.image_serial)
    )

    return ""

@colorizer.route("/incorrect-output/<id>", methods=["PATCH"])
@cross_origin()
def incorrect_output(id):

    # get the tag information
    tag_information = request.form
    
    # update the image with actual_main_tag
    image = Image.query.filter_by(id=id).first()

    # error if ID wasn't found
    if not image:
        raise Error(
            "Not_Found",
            "The image does not exist inside the database",
            404
        )

    # check if the required keys are there
    required_keys = ["actual_main_tag", "tags"]
    for key in required_keys:
        if key not in tag_information.keys():
            raise Error(
                "Unprocessable_Entity",
                "Please ensure key {} exists".format(key),
                422
            )

    actual_main_tags = tag_information["actual_main_tag"]
    tags = tag_information["tags"]
    
    # check request tags are valid (also checks types implicitly)
    if not reverse_tag_mappings.get(actual_main_tags):
        raise Error(
            "Nonexistent_Tag",
            "The Tag does not Exist",
            404
        )

    if not isinstance(tags, str):
        raise Error(
            "Wrong_Data_Type",
            "Ensure 'tags' is a str",
            422
        )

    # insert main actual tag into db
    image.actual_main_tag = reverse_tag_mappings[tag_information["actual_main_tag"]]
    insert_db(image)

    # check if tags exist
    tag_list = tags.split(",")
    for indiv_tag in tag_list:
        if not reverse_tag_mappings.get(indiv_tag):
            raise Error(
                "Nonexistent_Tag",
                "The Tag does not Exist",
                404
            )

    # places values in actual_tags table
    for tag_name in tag_list:
        actual_tags = ActualTags(image_id=image.id, tag_name=tag_name, tag_number=reverse_tag_mappings.get(tag_name))
        insert_db(actual_tags)

    # upload the image to ground truth folder
    try:
        file = request.files["image"]
    except KeyError:
        raise Error(
            "Unprocessable_Entity",
            "Please include an 'image' key in your request.",
            422
        )

    file.save(os.path.join(app.config["GROUND_TRUTH"], image.image_serial))

    return ""

@colorizer.route("/test", methods=["POST"])
@cross_origin()
def test():
    
    # print("\n\n\n")
    # print(request.data)
    # print(request.files)
    # print(request.form)
    # tagList = request.form["tags"].split(",")
    # for i in tagList:
    #     print(i)
    # print(request.args)
    # print(request.json)
    # print("\n\n\n")

    image = Image(original_name="William", image_serial=2)
    
    insert_db(image)

    return "success"
