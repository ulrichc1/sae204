import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import '../components/geography.css'; // Import your CSS file

mapboxgl.accessToken = 'pk.eyJ1IjoidWxyaWNoYzEiLCJhIjoiY2xpa3JxcDR2MDF0bDNrcG5lZmU4NTViNiJ9.siwlD23fTQzrsf5ywF56CQ';


const GeographyChart = () => {
    const mapContainer = useRef(null);
    const map = useRef(null);
    const [lng, setLng] = useState(2.3522);
    const [lat, setLat] = useState(48.8566);
    const [zoom, setZoom] = useState(12);


    useEffect(() => {
        if (!map.current) {
            map.current = new mapboxgl.Map({
                container: mapContainer.current,
                style: 'mapbox://styles/mapbox/light-v10',
                center: [lng, lat],
                zoom: zoom,
            });
        }
    }, []);

    useEffect(() => {
        if (!map.current) return;
        map.current.on('move', () => {
            setLng(map.current.getCenter().lng.toFixed(4));
            setLat(map.current.getCenter().lat.toFixed(4));
            setZoom(map.current.getZoom().toFixed(2));
        });
    });

    const fetchStationData = async () => {
        try {
            const response = await fetch('http://localhost:8800/station_information/paris');
            const data = await response.json();

            // Supprimer les marqueurs existants de la carte
            const markers = map.current.getMarkers();
            markers.forEach((marker) => marker.remove());

            data.forEach((station) => {
                new mapboxgl.Marker()
                    .setLngLat([station.lon, station.lat])
                    .setPopup(
                        new mapboxgl.Popup({ offset: 25 }).setHTML(
                            `<h3>${station.station_id}</h3><p>${station.name}</p>`
                        )
                    )
                    .addTo(map.current);
            });
        } catch (error) {
            console.error(error);
        }
    };

    useEffect(() => {
        fetchStationData();
    }, []);

    return (
        <div style={{ width: '100%', height: '100vh' }}>
            <div className="sidebar">
                Longitude: {lng} | Latitude: {lat} | Zoom: {zoom}
            </div>
            <div ref={mapContainer} style={{ width: '100%', height: 'calc(100% - 40px)' }} />
        </div>
    );
};

export default GeographyChart;