import requests
import json
import time
import datetime
import os
from subprocess import call

username = "_nazan_nur"
last_id = ""


def getFollowerCount(user):
    try:
        r = requests.get("https://www.instagram.com/" + user + "/")
    except requests.exceptions.ChunkedEncodingError:
        time.sleep(1)
        r = requests.get("https://www.instagram.com/" + user + "/")

    start = r.text.find("activity_counts") - 3
    end = r.text.find(";</script>", start)
    json_text = r.text[start:end]
    data = json.loads(json_text)
    return data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_followed_by"]["count"]


def getRecentMediaCodesAndIDs(user, lastMedia=''):
    try:
        r = requests.get("https://www.instagram.com/" + user + "/")
    except requests.exceptions.ChunkedEncodingError:
        time.sleep(1)
        r = requests.get("https://www.instagram.com/" + user + "/")

    start = r.text.find("activity_counts") - 3
    end = r.text.find(";</script>", start)
    json_text = r.text[start:end]
    data = json.loads(json_text)
    items = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
    media_codes = []
    for (i, item) in enumerate(items):
        if item["node"]["id"] == lastMedia:
            break
        media_codes.append((item["node"]["shortcode"], item["node"]["id"]))

    return media_codes


def getMediaInfo(code):
    try:
        r = requests.get("https://www.instagram.com/p/" + code + "/")
    except requests.exceptions.ChunkedEncodingError:
        time.sleep(1)
        r = requests.get("https://www.instagram.com/p/" + code + "/")

    start = r.text.find("activity_counts") - 3
    end = r.text.find(";</script>", start)
    json_text = r.text[start:end]
    data = json.loads(json_text)
    return data


def getMediaMentionsAndTags(code):
    try:
        r = requests.get("https://www.instagram.com/p/" + code + "/")
    except requests.exceptions.ChunkedEncodingError:
        time.sleep(1)
        r = requests.get("https://www.instagram.com/p/" + code + "/")

    start = r.text.find("activity_counts") - 3
    end = r.text.find(";</script>", start)
    json_text = r.text[start:end]
    data = json.loads(json_text)
    items = data["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["edge_media_to_tagged_user"]["edges"]
    users = []
    for (i, item) in enumerate(items):
        if item["node"]["user"]["username"] not in users:
            users.append(item["node"]["user"]["username"])

    items = data["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["edge_media_to_caption"]["edges"]
    for (i, item) in enumerate(items):
        users += getUsersInCaption(item["node"]["text"])

    return users


def getUsersInCaption(text):
    users = []
    ln = len(text)
    at_location = text.find("@")
    while at_location > 0:
        p = at_location + 1

        while p + 1 <= ln and isUserNameChar(text[p]):
            p = p + 1

        users.append(text[at_location+1:p])
        at_location = text.find("@", p)

    return users


def isUserNameChar(char):
    val = ord(char)
    if (val >= 48 and val >= 57) or (val >= 65 and val >= 90) or (val >= 97 and val >= 122):
        return True
    else:
        return False


def load_users(user):
    userlist = []
    try:
        fo = open(user + "_tracking.txt", "r", 100)
        for line in fo:
            if line.strip() != "":
                userlist.append(line.strip())
        fo.close()
    except FileNotFoundError as e:
        print("Warning: " + user + "_tracking.txt file not found. Going to be created.")
    return userlist


def save_users(user, userlist):
    fo = open(user + "_tracking.txt", "w", 100)
    for u in userlist:
        fo.write(u + "\n")
    fo.close()


def saveCountForUser(user, tracked_user, last_count, tagged_again):
    fo = open(user + "_" + tracked_user + ".txt", "a", 100)
    fo.write(str(last_count) + "\t" + str(datetime.datetime.now()) + "\t" + str(tagged_again) + "\n")
    fo.close()


# retval = getRecentMediaCodesAndIDs(username, "1619092965199471379")
#
# last_id = retval[0][1]
#
# for val in retval:
#     print(getMediaMentionsAndTags(val[0]))
#
# print(retval)
# print(last_id)

username = input("Instagram account name to be tracked: ")
check_int = int(input("Seconds between every control: "))

while True:
    if os.name == 'nt':
        os.system('cls')
    else:
        call(["clear"])

    print("> Getting information of user " + username)
    # load tracked user list
    tracked_users = load_users(username)

    # get recent media codes starting  from last_id
    media_codes = getRecentMediaCodesAndIDs(username, last_id)
    print("> " + str(len(media_codes)) + " new media found. Checking connected users...")
    # update last_id
    if len(media_codes) > 0:
        last_id = media_codes[0][1]

    for media in media_codes:
        # get mentioned and tagged users for each media
        users = getMediaMentionsAndTags(media[0])

        # and for each user if the user isn't in track list then add to the list and update file
        user_added = False
        for user in users:
            if user not in tracked_users:
                tracked_users.append(user)
                user_added = True
                print("> @" + user + " added to tracking list.")

        if user_added:
            save_users(username, tracked_users)

    print("> Looking for follower counts for users:")
    for tracked_user in tracked_users:
        print(">>> " + tracked_user)
        follower_count = getFollowerCount(tracked_user)
        saveCountForUser(username, tracked_user, follower_count, tracked_user in users)

    print("> Process completed. Sleeping for " + str(check_int) + " seconds...")
    # for each user on the list get follower count and append the value with time on the corresponding users file
    time.sleep(check_int)