const {
  extractText,
  getCleanNumber,
  isValueInsidePolygon,
  downloadImage,
} = require("./helpers");

exports.handler = async function (event, context) {
  console.log(event);
  const { id, resultados } = event;
  const response = {
    id,
    votosEnTotal: -1,
    votosImpugnados: -1,
    votosEnBlancos: -1,
    votosRecurridos: -1,
    votosNulos: -1,
    conteo: {
      lla: -1,
      up: -1,
    },
    esValido: false,
  };

  // request and download the image
  const encodingBinary = await downloadImage(payload.imageURL);
  const buffer = Buffer.from(encodingBinary, "base64");
  const imagePage = await sharp(buffer, { page: 0 }).toBuffer();

  // extract the text
  const results = await extractText(imagePage);
  const { Blocks } = results;

  // iterate through returned blocks from Textract
  for (const block of Blocks) {
    const {
      Confidence,
      Geometry: { BoundingBox },
      Text: extractedText,
    } = block;

    // less than 50% is not trusty
    if (Confidence < 50 || !extractedText) continue;

    // coords of the text in the image
    const left = BoundingBox.Left;
    const top = BoundingBox.Top;

    // total
    if (isValueInsidePolygon("votosEnTotal", [left, top])) {
      response.votosEnTotal = getCleanNumber(extractedText);
    }

    // LLA
    if (
      !response.conteo.lla &&
      isValueInsidePolygon("votosTelegramaLLA", [left, top])
    ) {
      response.conteo.lla = getCleanNumber(extractedText);
    }

    // UP
    if (
      !response.conteo.up &&
      isValueInsidePolygon("votosTelegramaUP", [left, top])
    ) {
      response.conteo.up = getCleanNumber(extractedText);
    }

    // votos impugnados
    if (isValueInsidePolygon("votosImpugnados", [left, top])) {
      response.votosImpugnados = extractedText;
    }

    // votos en blancos
    if (isValueInsidePolygon("votosEnBlancos", [left, top])) {
      response.votosEnBlancos = extractedText;
    }

    // votos recurridos
    if (isValueInsidePolygon("votosRecurridos", [left, top])) {
      response.votosRecurridos = extractedText;
    }
  }

  response.esValido =
    response.conteo.lla == resultados.lla &&
    response.conteo.up == resultados.up;

  return response;
};
