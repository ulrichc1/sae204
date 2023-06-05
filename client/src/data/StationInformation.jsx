import { Box, Typography, useTheme } from '@mui/material';
import {DataGrid, GridToolbar} from '@mui/x-data-grid';
import Header from '../components/Header';
import { useEffect, useState } from 'react';

const StationInformation = () => {
    const theme = useTheme();
    const columns = [
        { field: 'station_id', headerName: 'ID'},
        { field: 'name', headerName: 'Station Name', flex: 1, cellClassName: "name-column--cell" },
        { field: 'lat', headerName: 'Latitude', flex: 1 },
        { field: 'lon', headerName: 'Longitude', flex: 1},
        { field: 'capacity', headerName: 'Capacity', flex: 1, type: "number" },
    ];

    const [rows, setRows] = useState([]);

    useEffect(() => {
        fetch('http://localhost:8800/station_information')
            .then(response => response.json())
            .then(data => setRows(data))
            .catch(error => console.error('Error fetching data:', error));
    }, []);

    const getRowId = (row) => row.station_id; // Assuming station_id is a unique identifier

    return (
        <Box>
            <Header title="Stations - Info" subtitle="Informations sur les stations Vélib'Métropole"/>
            <Box>
                <DataGrid
                    rows={rows}
                    columns={columns}
                    getRowId={getRowId}
                />
            </Box>
        </Box>
    );
};

export default StationInformation;