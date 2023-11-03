const { fromEnv } = require("@aws-sdk/credential-providers");
const {
  TextractClient,
  DetectDocumentTextCommand,
} = require("@aws-sdk/client-textract");
const pointInPolygon = require("point-in-polygon");
const BOXES = require("./boxes");

const downloadImage = async (url) => {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const buffer = await response.buffer();
    return buffer;
  } catch (error) {
    console.error("Error downloading image:", error);
    throw error;
  }
};

const getCleanNumber = (value) => {
  const number = parseInt(value);
  if (isNaN(number)) {
    const mapping = {
      o: 0,
      l: 1,
      z: 2,
      e: 9,
      a: 4,
      s: 5,
      g: 9,
      b: 6,
      "|": 1,
      "/": 1,
      "\\": 1,
    };
    let result = "";
    for (let char of value.toLowerCase()) {
      if (mapping[char] !== undefined) {
        result += mapping[char];
      } else {
        result += char;
      }
    }

    return parseInt(result);
  }

  return number;
};

const Textract = new TextractClient({
  region: "us-east-1",
  credentials: fromEnv(),
});
const extractText = async (buffer) => {
  const command = new DetectDocumentTextCommand({
    Document: {
      Bytes: buffer,
    },
  });
  const data = await Textract.send(command);
  return data;
};

const isValueInsidePolygon = (fieldKey, points) => {
  const boxes = BOXES[fieldKey];
  for (const box of boxes) {
    if (pointInPolygon(points, box)) {
      return true;
    }
  }

  return false;
};

module.exports = {
  getCleanNumber,
  extractText,
  isValueInsidePolygon,
  downloadImage,
};
