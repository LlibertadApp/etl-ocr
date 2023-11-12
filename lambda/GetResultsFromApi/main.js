exports.handler = async function (event, context) {
  const { id } = event;
  if (!id) {
    throw new Error("Invalid id");
  }

  const getScopeData = await fetch(
    `https://resultados.gob.ar/backend-difu/scope/data/getScopeData/${id}/1`
  );
  const scopeData = await getScopeData.json();
  const {
    partidos,
    recurridos,
    blancos,
    impugnados,
    nulos,
    electores,
    sobres,
    totalVotos,
  } = scopeData;
  const lla = partidos.find((p) => p.code == "135");
  const up = partidos.find((p) => p.code == "134");

  if (process.env.USE_DUMMY_FILE) {
    const dummy = require("../../dummy.json");
    return dummy.GetResultsFromApi;
  }

  return {
    id,
    partidos,
    resultados: { lla, up },
    recurridos,
    blancos,
    impugnados,
    nulos,
    electores,
    sobres,
    totalVotos,
  };
};
