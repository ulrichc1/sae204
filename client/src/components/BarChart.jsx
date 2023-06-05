import { useTheme, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button } from "@mui/material";
import { ResponsiveBar } from "@nivo/bar";
import { tokens } from "../theme";
import { useState, useEffect } from "react";
const BarChart = ({ isDashboard = false }) => {
    const [data, setData] = useState([]);
    const theme = useTheme();
    const [open, setOpen] = useState(false); // state pour contrôler l'ouverture du pop-up
    const [popupData, setPopupData] = useState(null); // state pour stocker les données du pop-up
    const colors = tokens(theme.palette.mode);

    useEffect(() => {
        fetch('http://localhost:8800/station_status/districts')
            .then(response => response.json())
            .then(data => setData(data))
            .catch(error => console.error('Error fetching data:', error));
    }, []);

    const handleBarClick = (event) => {
        // Récupérer les données du bar correspondant au clic
        const { id, value, indexValue } = event.data;

        // Mettre à jour les données du pop-up
        setPopupData({ id, value, indexValue });

        // Ouvrir le pop-up
        setOpen(true);
    };

    const handleClose = () => {
        // Fermer le pop-up
        setOpen(false);
    };

    const handleButtonClick = () => {
        // Ouvrir le pop-up lorsque le bouton est cliqué
        setOpen(true);
    };



    return (
        <>
            <div style={{display: "flex", justifyContent: "flex-end" }}>
                <Button onClick={handleButtonClick} variant="contained" color="primary">
                    More info
                </Button>
            </div>
                <Dialog open={open} onClose={handleClose}>
                    <DialogTitle>District info</DialogTitle>
                    <DialogContent>
                        <DialogContentText>
                            <table>
                                <thead>
                                <tr>
                                    <th>District</th>
                                    <th>Electric bikes</th>
                                    <th>Mechanical bikes</th>
                                </tr>
                                </thead>
                                <tbody>
                                {data.map((item) => (
                                    <tr key={item.district_name}>
                                        <td>{item.district_name}</td>
                                        <td>{item.available_electric_bikes}</td>
                                        <td>{item.available_mechanical_bikes}</td>
                                    </tr>
                                ))}
                                </tbody>
                            </table>
                        </DialogContentText>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleClose}>Fermer</Button>
                    </DialogActions>
                </Dialog>
        <ResponsiveBar
            data={data}
            onClick={handleBarClick} // Ajouter l'event handler pour le clic sur les bars

            theme={{
                // added
                axis: {
                    domain: {
                        line: {
                            stroke: colors.grey[100],
                        },
                    },
                    legend: {
                        text: {
                            fill: colors.grey[100],
                        },
                    },
                    ticks: {
                        line: {
                            stroke: colors.grey[100],
                            strokeWidth: 1,
                        },
                        text: {
                            fill: colors.grey[100],
                        },
                    },
                },
                legends: {
                    text: {
                        fill: colors.grey[100],
                    },
                },
            }}
            keys={["available_electric_bikes", "available_mechanical_bikes"]}
            indexBy="district_name"
            margin={{ top: 50, right: 130, bottom: 50, left: 60 }}
            padding={0.3}
            valueScale={{ type: "linear" }}
            indexScale={{ type: "band", round: true }}
            colors={{ scheme: "paired" }}
            defs={[
                {
                    id: "dots",
                    type: "patternDots",
                    background: "inherit",
                    color: "#38bcb2",
                    size: 4,
                    padding: 1,
                    stagger: true,
                },
                {
                    id: "lines",
                    type: "patternLines",
                    background: "inherit",
                    color: "#eed312",
                    rotation: -45,
                    lineWidth: 6,
                    spacing: 10,
                },
            ]}
            borderColor={{
                from: "color",
                modifiers: [["darker", "1.6"]],
            }}
            axisTop={null}
            axisRight={null}
            axisBottom={{
                tickSize: 5,
                tickPadding: 5,
                tickRotation: 0,
                legend: isDashboard ? undefined : "Districts", // changed
                legendPosition: "middle",
                legendOffset: 32,
            }}
            axisLeft={{
                tickSize: 5,
                tickPadding: 5,
                tickRotation: 0,
                legend: isDashboard ? undefined : "Availability", // changed
                legendPosition: "middle",
                legendOffset: -40,
            }}
            enableLabel={false}
            labelSkipWidth={12}
            labelSkipHeight={12}
            labelTextColor={{
                from: "color",
                modifiers: [["darker", 1.6]],
            }}
            legends={[
                {
                    dataFrom: "keys",
                    anchor: "bottom-right",
                    direction: "column",
                    justify: false,
                    translateX: 120,
                    translateY: 0,
                    itemsSpacing: 2,
                    itemWidth: 100,
                    itemHeight: 20,
                    itemDirection: "left-to-right",
                    itemOpacity: 0.85,
                    symbolSize: 20,
                    effects: [
                        {
                            on: "hover",
                            style: {
                                itemOpacity: 1,
                            },
                        },
                    ],
                },
            ]}
            role="application"
            barAriaLabel={function (e) {
                return e.id + ": " + e.formattedValue + " in stations: " + e.indexValue;
            }}
        />
        </>
    );
};

export default BarChart;