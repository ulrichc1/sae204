import { Box } from "@mui/material";
import Header from "../../components/Header";
import PieChart from "../../components/PieChart";
import {useEffect, useState} from "react";

const Pie = () => {
    return (
        <Box m="20px">
            <Header title="Pie Chart" subtitle=" Pie Chart" />
            <Box height="75vh">

                </div>
                <PieChart />
            </Box>
        </Box>
    );
};

export default Pie;