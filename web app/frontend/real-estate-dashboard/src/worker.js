onmessage = function(event) {
  const { locations } = event.data;
  const processedData = locations.map(location => {
    const lat = parseFloat(location.latitude);
    const lng = parseFloat(location.longitude);
    if (!isNaN(lat) && !isNaN(lng)) {
      return [lat, lng, 1]; // weight of the point
    }
    return null;
  }).filter(Boolean); // Remove any null values
  postMessage(processedData);
};
