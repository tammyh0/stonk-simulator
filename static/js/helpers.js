// Get list of current US stock symbols and names
let currentStocks = [];
const getCurrentStocks = () => {
  fetch('https://finnhub.io/api/v1/stock/symbol?exchange=US&token=c3nlhsaad3iabnjjd4c0')
    .then(response => {
      if (!response.ok) {
        console.log("Status error");
        return;
      } 
      
      return response.json();
    })
    .then(data => {
      data.forEach(stock => {
        let stockInfo = {};
        stockInfo["symbol"] = stock["displaySymbol"];
        stockInfo["name"] = stock["description"];
        currentStocks.push(stockInfo);
      });
    })
    .catch(err => console.log(err));
}


// Remove all child nodes
const removeChildren = (parent) => {
  while (parent.firstChild) {
    parent.removeChild(parent.firstChild);
  }
}

export { currentStocks, getCurrentStocks, removeChildren };
