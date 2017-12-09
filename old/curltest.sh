curl -XPOST localhost:5000/parse -d '{"q":"clear the playlist"}' | python -mjson.tool
curl -XPOST localhost:5000/parse -d '{"q":"yes"}' | python -mjson.tool
curl -XPOST localhost:5000/parse -d '{"q":"create a playlist called jugs"}' | python -mjson.tool


