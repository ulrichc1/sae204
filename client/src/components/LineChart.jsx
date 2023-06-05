import { ResponsiveLine } from '@nivo/line'
import {useEffect, useState} from "react";
import {tokens} from "../theme";
import { useTheme, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button } from "@mui/material";

const LineChart = () => {
    const theme = useTheme();
    const [data, setData] = useState([]);
    const [popupData, setPopupData] = useState([]); // state pour stocker les données du pop-up
    const [open, setOpen] = useState(false); // state pour contrôler l'ouverture du pop-up
    const colors = tokens(theme.palette.mode);

        useEffect(() => {
            async function fetchDataFromAPI() {
                try {
                    const response = await fetch('http://localhost:8800/station_status/bikes_count');
                    const jsonData = await response.json();

                    const convertedData = convertJSON(jsonData);
                    setPopupData(popConvertJSON(jsonData));
                    setData(convertedData);
                } catch (error) {
                    console.error('Erreur lors de la récupération des données depuis l\'API:', error);
                }
            }

            fetchDataFromAPI();
        }, []);

    const handleClose = () => {
        // Fermer le pop-up
        setOpen(false);
    };

    const handleButtonClick = () => {
        // Ouvrir le pop-up lorsque le bouton est cliqué
        setOpen(true);
    };



    function convertJSON(jsonData) {
            const result = [];
            const dataMap = new Map();

            function formatDate(dateString) {
                const date = new Date(dateString);
                const day = String(date.getDate()).padStart(2, '0');
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const year = date.getFullYear();
                const hours = String(date.getHours()).padStart(2, '0');
                const minutes = String(date.getMinutes()).padStart(2, '0');
                const formattedDate = `${day}-${month}-${year} ${hours}:${minutes}`;
                return formattedDate;
            }

            for (const item of jsonData) {
                const { id, total_available_bikes, x } = item;
                const formattedDate = formatDate(x);

                if (!dataMap.has(id)) {
                    const data = {
                        id,
                        color: colors.greenAccent[500],
                        data: []
                    };
                    result.push(data);
                    dataMap.set(id, data.data);
                }

                const data = {
                    x: formattedDate,
                    y: total_available_bikes
                };
                dataMap.get(id).push(data);
            }
            console.log(result);
            return result;
        }

    function popConvertJSON(jsonData) {
        const formattedData = jsonData.map(item => {
            return {
                x: item.x,
                electricBikes: item.total_available_bikes,
                mechanicalBikes: item.total_available_bikes,
            };
        });

        return formattedData;
    }
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
                        <table>
                            <thead>
                            <tr>
                                <th>Date</th>
                                <th>Electric bikes</th>
                                <th>Mechanical bikes</th>
                            </tr>
                            </thead>
                            <tbody>
                            {popupData.map(item => (
                                <tr key={item.x}>
                                    <td>{item.x}</td>
                                    <td>{item.electricBikes}</td>
                                    <td>{item.mechanicalBikes}</td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleClose}>Fermer</Button>
                    </DialogActions>
                </Dialog>


            <ResponsiveLine
                data={data}
                margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
        xScale={{ type: 'point' }}
        yScale={{
            type: 'linear',
            min: 'auto',
            max: 'auto',
            stacked: true,
            reverse: false
        }}
        yFormat=" >-.2f"
        axisTop={null}
        axisRight={null}
        axisBottom={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Date & Hour',
            legendOffset: 36,
            legendPosition: 'middle'
        }}
        axisLeft={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Number of bikes',
            legendOffset: -50,
            legendPosition: 'middle'
        }}
        colors={{ scheme: 'paired' }}
        pointSize={10}
        pointColor={{ theme: 'background' }}
        pointBorderWidth={2}
        pointBorderColor={{ from: 'serieColor' }}
        pointLabelYOffset={-12}
        useMesh={true}
        legends={[
            {
                anchor: 'bottom-right',
                direction: 'column',
                justify: false,
                translateX: 82,
                translateY: -45,
                itemsSpacing: 0,
                itemDirection: 'left-to-right',
                itemWidth: 80,
                itemHeight: 20,
                itemOpacity: 0.75,
                symbolSize: 12,
                symbolShape: 'circle',
                symbolBorderColor: 'rgba(0, 0, 0, .5)',
                effects: [
                    {
                        on: 'hover',
                        style: {
                            itemBackground: 'rgba(0, 0, 0, .03)',
                            itemOpacity: 1
                        }
                    }
                ]
            }
        ]}
    />
            </>);
}

export default LineChart;