const { fromEnv } = require("@aws-sdk/credential-providers");
const {
  TextractClient,
  DetectDocumentTextCommand,
} = require("@aws-sdk/client-textract");
// const pointInPolygon = require("point-in-polygon");
const pointInPolygon = require("point-in-polygon-hao");
const sharp = require("sharp");
const axios = require("axios");

const coords = {
  up: [
    [
      [0.01333, 0.00735],
      [0.99333, 0.00735],
      [0.99333, 0.14338],
      [0.01333, 0.14338],
    ],
  ],
  lla: [
    [
      [0.01333, 0.14154],
      [0.99, 0.14154],
      [0.99, 0.14154],
      [0.01333, 0.28676],
    ],
  ],
  nulos: [
    [
      [0.01333, 0.28676],
      [0.99, 0.28676],
      [0.99, 0.43382],
      [0.01333, 0.43382],
    ],
  ],
  recurridos: [
    [
      [0.00667, 0.43199],
      [0.99, 0.43199],
      [0.99, 0.58088],
      [0.00667, 0.58088],
    ],
  ],
  impugnados: [
    [
      [0.00667, 0.57537],
      [0.99667, 0.57537],
      [0.99667, 0.72059],
      [0.00667, 0.72059],
    ],
  ],
  blancos: [
    [
      [0.00333, 0.72059],
      [1, 0.71507],
      [1, 0.86765],
      [0.00333, 0.86765],
    ],
  ],
  total: [
    [
      [0.00667, 0.86581],
      [1, 0.86581],
      [1, 0.99632],
      [0.00667, 0.99632],
    ],
  ],
};

exports.handler = async function (event, context) {
  const { image } = event;
  const response = {
    up: -1,
    lla: -1,
    nulos: -1,
    recurridos: -1,
    impugnados: -1,
    blancos: -1,
    total: -1,
  };

  // request and download the image
  const encodingBinary = await downloadImage(image);
  const buffer = Buffer.from(encodingBinary, "base64");
  const imagePage = await sharp(buffer, { page: 0 }).toBuffer();

  // extract the text
  const results = await extractText(imagePage);
  const { Blocks } = results;
  const words = Blocks.filter(
    (block) =>
      block.BlockType === "WORD" &&
      block.Geometry.BoundingBox.Left.toFixed(2) > 0.0
  );

  // iterate through returned blocks from Textract
  for (const block of words) {
    const {
      Confidence,
      Geometry: { BoundingBox },
      Text: extractedText,
    } = block;

    // less than 51% is not trusty
    if (Confidence < 51 || !extractedText) continue;

    // coords of the text in the image
    const left = BoundingBox.Left;
    const top = BoundingBox.Top;
    for (const field in response) {
      const isInside = isValueInsidePolygon(field, [left, top]);
      if (isInside) {
        response[field] = getCleanNumber(extractedText);
      }
      // console.log(extractedText, isInside);
    }
  }

  return response;
};

const downloadImage = async (url) => {
  const response = await axios({
    url,
    method: "get",
    responseType: "arraybuffer",
  });
  if (response.status != 200) {
    throw new Error(`Error bajando imagen: ${response.status}`);
  }

  return Buffer.from(response.data, { encoding: "binary" });
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
  region: process.env.REGION,
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
  const polygons = coords[fieldKey];
  if (!polygons) {
    throw Error(`Coordenadas no encontradas: ${fieldKey}`);
  }

  try {
    return pointInPolygon(points, polygons);
  } catch (err) {}
};
