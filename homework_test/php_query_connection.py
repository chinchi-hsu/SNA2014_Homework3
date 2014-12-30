import http.client;
import sys;

if len(sys.argv) < 2:
    print("Usage: python3 query.py team [node]");
    quit();

team = sys.argv[1];
node = "";
if len(sys.argv) > 2:
    node = sys.argv[2];

url= "/SNA2014/hw3/query.php?team=" + team;
if node != "":
    url += "&node=" + node;

connection = http.client.HTTPConnection("140.112.31.186", 80);
connection.request("GET", url);
response = connection.getresponse();
data = response.read().decode("utf-8");

print(data);
