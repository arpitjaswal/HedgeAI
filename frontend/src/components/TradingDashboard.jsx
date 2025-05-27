import React, { useState } from 'react';

const TradingDashboard = ({
  symbols = ["BINANCE:BTCUSDT", "BINANCE:SOLUSDT"],
  timeframes = ["1", "5", "15", "60"],
}) => {
  const [selectedSymbol, setSelectedSymbol] = useState(symbols[0]);
  const [selectedTimeframe, setSelectedTimeframe] = useState(timeframes[0]);
const [analysisResult, setAnalysisResult] = useState(null);

  const getWidgetUrl = (symbol, interval) =>
    `https://www.tradingview.com/widgetembed/?frameElementId=tv_${symbol}_${interval}&symbol=${symbol}&interval=${interval}&theme=dark&style=1&timezone=Etc%2FUTC&saveimage=1&toolbarbg=f1f3f6&studies=[]&withdateranges=1&hideideas=1&enabled_features=%5B%22study_templates%22%5D`;

 const handleAnalyze = async () => {
  try {
    const res = await fetch(
      `http://localhost:8000/analyze/?symbol=${selectedSymbol}&interval=${selectedTimeframe}`
    );
    const data = await res.json();
    console.log("Gemini Analysis Result:", data);
    setAnalysisResult(data);
  } catch (err) {
    console.error("Error analyzing chart:", err);
    setAnalysisResult({ error: "Failed to analyze chart." });
  }
};


  return (
    <div className="bg-gray-900 min-h-screen p-6 text-white flex flex-col items-center">
      <div className="w-full max-w-4xl bg-gray-800 p-6 rounded-xl shadow-md mb-6">
        <h1 className="text-2xl font-bold mb-4 text-center">HedgeAI</h1>
        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Select Symbol</label>
            <select
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              className="w-full bg-gray-700 text-white px-4 py-2 rounded-md shadow focus:outline-none"
            >
              {symbols.map((symbol) => (
                <option key={symbol} value={symbol}>
                  {symbol.replace("BINANCE:", "")}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Select Timeframe (min)</label>
            <select
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              className="w-full bg-gray-700 text-white px-4 py-2 rounded-md shadow focus:outline-none"
            >
              {timeframes.map((tf) => (
                <option key={tf} value={tf}>
                  {tf}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="mt-6 text-center">
          <button
            onClick={handleAnalyze}
            className="bg-blue-600 hover:bg-blue-700 transition px-6 py-2 rounded-md text-white font-semibold shadow"
          >
            Analyze Chart
          </button>
        </div>
      </div>

      <div className="w-full max-w-4xl bg-gray-800 rounded-lg shadow p-4">
        <h2 className="text-center mb-4 text-lg font-semibold">
          {selectedSymbol.replace("BINANCE:", "")} — {selectedTimeframe} min
        </h2>
        <iframe
          title={`chart-${selectedSymbol}-${selectedTimeframe}`}
          src={getWidgetUrl(selectedSymbol, selectedTimeframe)}
          width="100%"
          height="500"
          frameBorder="0"
          allowTransparency="true"
          scrolling="no"
          className="rounded"
        />
        {analysisResult && (
  <div className="w-full max-w-4xl bg-gray-800 mt-6 rounded-lg shadow p-6">
    <h2 className="text-xl font-semibold mb-4 text-center text-blue-400">Gemini AI Analysis</h2>

    {analysisResult.error ? (
      <p className="text-red-400 text-center">{analysisResult.error}</p>
    ) : (
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm text-gray-200">
        <div>
          <strong>Trade Signal:</strong>{" "}
          <span className={`font-semibold ${analysisResult.trade_signal === "LONG" ? "text-green-400" : analysisResult.trade_signal === "SHORT" ? "text-red-400" : "text-yellow-400"}`}>
            {analysisResult.trade_signal}
          </span>
        </div>
        <div>
          <strong>Pattern:</strong> {analysisResult.pattern}
        </div>
        <div>
          <strong>Entry:</strong> {analysisResult.entry ?? "N/A"}
        </div>
        <div>
          <strong>Stop Loss:</strong> {analysisResult.stop_loss ?? "N/A"}
        </div>
        <div>
          <strong>Take Profit:</strong> {analysisResult.take_profit ?? "N/A"}
        </div>
        <div>
          <strong>Confidence:</strong>{" "}
          <span
            className={`font-semibold ${
              analysisResult.confidence === "High"
                ? "text-green-400"
                : analysisResult.confidence === "Medium"
                ? "text-yellow-400"
                : "text-red-400"
            }`}
          >
            {analysisResult.confidence}
          </span>
        </div>
      </div>
    )}
  </div>
)}
      </div>
    </div>
  );
};

export default TradingDashboard;
