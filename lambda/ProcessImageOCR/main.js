exports.handler = async function (event, context) {
  const { ProcessImageOCR } = event;

  const { count } = ProcessImageOCR;
  const OCRS_AVAILABLE = [];

  return {
    count: count + 1,
    completed: count === OCRS_AVAILABLE.length,
  };
};
