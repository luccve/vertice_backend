async function dados() {
  try {
    let response = await fetch(
      "https://www3.bcb.gov.br/vet/rest/v2/ranking?mesAno=022017&valor=100&moeda=USD&finalidade=1&tipoOperacao=C&formaDeEntrega=1",
      { method: "get" }
    );
    let dados_response = response.json();
    console.log(dados_response);
    return dados_response;
  } catch (err) {
    throw err;
  }
}

dados();
