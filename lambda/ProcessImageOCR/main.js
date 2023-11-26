const { Lambda } = require("aws-sdk");

// usar los nombres de lambda
const OCR_KEYS = {
  // LLM: "llm",
  AWS: "DetectTextAwsTextract",
  AZURE: "DetectTextAzureAI",
};

exports.handler = async function (event, context) {
  const { ProcessImageOCR, ExtractVotesNumbersFromImage } = event;
  const { image, cells } = ExtractVotesNumbersFromImage;
  const { count, data } = ProcessImageOCR;
  const OCRS_AVAILABLE = [
    // OCR_KEYS.LLM,
    OCR_KEYS.AWS,
    OCR_KEYS.AZURE,
  ];
  console.log(`Requesting OCR`, OCRS_AVAILABLE[count]);
  const extractedData = await requestDataToOcr(OCRS_AVAILABLE[count], {
    image,
    cells,
  });

  return {
    count: count + 1,
    extracted: checkIfWeExtractedAllFields(extractedData),
    wasted: count == OCRS_AVAILABLE.length - 1,
    data: Object.assign(data, extractedData),
  };
};

function checkIfWeExtractedAllFields(data) {
  for (const [key, value] of Object.entries(data)) {
    if (value === -1) {
      return false;
    }
  }

  return true;
}

async function requestDataToOcr(functionName, payload) {
  console.log("Calling function", functionName, payload);
  const { Payload } = await new Lambda()
    .invoke({
      FunctionName: `etl-ocr-${process.env.ENV}-${functionName}`,
      Payload: JSON.stringify(payload),
      InvocationType: "RequestResponse",
    })
    .promise();

  return JSON.parse(Payload);
}
