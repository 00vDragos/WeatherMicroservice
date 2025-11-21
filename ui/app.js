const button = document.getElementById("getWeatherBtn");
const cityInput = document.getElementById("cityInput");
const info = document.getElementById("weatherInfo");
const ctx = document.getElementById("tempChart").getContext("2d");
let chart = null;

button.addEventListener("click", async () => {
  const city = cityInput.value.trim();
  if (!city) {
    info.innerHTML = "<p>Please enter a city name.</p>";
    return;
  }

  try {
    const res = await fetch(`/api/weather?city=${city}`);
    if (!res.ok) throw new Error("City not found or API error");

    const data = await res.json();

    if (Array.isArray(data) && data.length > 0) {
      const latest = data[data.length - 1];
      info.innerHTML = `
        <h3>Weather in ${latest.city}</h3>
        <p>Temperature: ${latest.temperature} °C</p>
        <p>Humidity: ${latest.humidity}%</p>
        <p>Conditions: ${latest.description}</p>
        <p>Wind Speed: ${latest.wind_speed} m/s</p>
      `;

      // Data for chart
      const labels = data.map((item) =>
        new Date(item.timestamp).toLocaleTimeString()
      );
      const temps = data.map((item) => item.temperature);

      if (chart) chart.destroy();

      chart = new Chart(ctx, {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: "Temperature (°C)",
              data: temps,
              borderColor: "#4a90e2",
              fill: false,
              tension: 0.2,
            },
          ],
        },
        options: {
          scales: {
            x: { display: true, title: { display: true, text: "Time" } },
            y: { display: true, title: { display: true, text: "Temperature (°C)" } },
          },
        },
      });
    } else {
      info.innerHTML = "<p>No data found for this city yet.</p>";
    }
  } catch (err) {
    info.innerHTML = `<p style="color:red;">Error: ${err.message}</p>`;
  }
});
