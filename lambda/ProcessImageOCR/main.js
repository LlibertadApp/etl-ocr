const OCR_KEYS = {
  LLM: "llm",
};

exports.handler = async function (event, context) {
  const { ProcessImageOCR } = event;
  const { count, data } = ProcessImageOCR;
  const OCRS_AVAILABLE = [OCR_KEYS.LLM];
  const extractedData = requestDataToOcr(OCRS_AVAILABLE[count]);

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

function requestDataToOcr(ocr) {
  switch (ocr) {
    case OCR_KEYS.LLM: {
      return {};
    }
  }
}
