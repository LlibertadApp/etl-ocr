const {
  AzureKeyCredential,
  DocumentAnalysisClient,
} = require("@azure/ai-form-recognizer");

exports.handler = async function (event) {
  const { AZURE_AI_ENDPOINT, AZURE_AI_KEY, AZURE_AI_MODEL_ID } = process.env;
  const client = new DocumentAnalysisClient(
    AZURE_AI_ENDPOINT,
    new AzureKeyCredential(AZURE_AI_KEY)
  );

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

  const poller = await client.beginAnalyzeDocumentFromUrl(
    AZURE_AI_MODEL_ID,
    image
  );
  const {
    documents: [document],
  } = await poller.pollUntilDone();

  for (const field in response) {
    const extractedField = document.fields[field];
    if (extractedField) {
      const extractedValue = extractedField.content;
      if (!isNaN(extractedValue)) {
        response[field] = parseInt(extractedField.content);
      }
    }
  }

  return response;
};
