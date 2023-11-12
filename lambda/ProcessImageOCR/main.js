const { Lambda } = require("aws-sdk");

// usar los nombres de lambda
const OCR_KEYS = {
  // LLM: "llm",
  AWS: "DetectTextAwsTextract",
};

exports.handler = async function (event, context) {
  const { ProcessImageOCR } = event;
  const { count, data } = ProcessImageOCR;
  const OCRS_AVAILABLE = [OCR_KEYS.LLM];
  const extractedData = await requestDataToOcr(OCRS_AVAILABLE[count]);

  return {
    count: count + 1,
    extracted: checkIfWeExtractedAllFields(data),
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

async function requestDataToOcr(lambda) {
  const extracted = await new Lambda()
    .invoke({
      FunctionName: lambda,
      Payload: JSON.stringify({}),
      InvocationType: "RequestResponse",
    })
    .promise();

  return extracted;
}
