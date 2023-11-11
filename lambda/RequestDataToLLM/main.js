exports.handler = async (event) => {
  const { LLM_ENDPOINT } = process.env;
  const { data } = await fetch(`${LLM_ENDPOINT}`);
  return data;
};
