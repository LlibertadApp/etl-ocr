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

  return {
    id,
    resultados: partidos,
    recurridos,
    blancos,
    impugnados,
    nulos,
    electores,
    sobres,
    totalVotos,
  };
};
