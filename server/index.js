const express = require('express');
const db = require('./config/db');
const cors = require('cors');
const app = express();
const PORT = 8800;
const cache = {};

app.use(cors());
app.use(express.json());

// Fonction pour vider le cache
/* function clearCache() {
    cache.station_status = null;
    cache.last24Hours = null;
    cache.last48Hours = null;
    cache.lastWeek = null;
    cache.pie_data = null;
    cache.station_information = null;
    cache.districts_list = null;
}

// Planification pour vider le cache toutes les 10 minutes
setInterval(clearCache, 10 * 60 * 1000);
*/

app.get("/", (req, res) => {
    res.send("MySQL Server is running");
});

app.get("/station_status", (req, res) => {
    // Check if the data is already cached
    if (cache.station_status) {
        res.send(cache.station_status);
    } else {
        db.query("SELECT station_id, available_docks, available_electric_bikes, available_mechanical_bikes, available_bikes, status, MAX(last_update) as last_update, district_name FROM station_status GROUP BY station_id", (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data
                cache.station_status = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/last_24_hours", (req, res) => {
    // Check if the data is already cached
    if (cache.last24Hours) {
        res.send(cache.last24Hours);
    } else {
        const last24HoursQuery = "SELECT station_id, available_docks, available_electric_bikes, available_mechanical_bikes, available_bikes, status, last_update, district_name FROM station_status WHERE last_update >= DATE_SUB(NOW(), INTERVAL 24 HOUR)";

        db.query(last24HoursQuery, (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data
                cache.last24Hours = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/last_48_hours", (req, res) => {
    // Check if the data is already cached
    if (cache.last48Hours) {
        res.send(cache.last48Hours);
    } else {
        const last48HoursQuery = "SELECT station_id, available_docks, available_electric_bikes, available_mechanical_bikes, available_bikes, status, last_update, district_name FROM station_status WHERE last_update >= DATE_SUB(NOW(), INTERVAL 48 HOUR)";

        db.query(last48HoursQuery, (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data
                cache.last48Hours = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/last_week", (req, res) => {
    // Check if the data is already cached
    if (cache.lastWeek) {
        res.send(cache.lastWeek);
    } else {
        const lastWeekQuery = "SELECT station_id, available_docks, available_electric_bikes, available_mechanical_bikes, available_bikes, status, last_update, district_name FROM station_status WHERE last_update >= DATE_SUB(NOW(), INTERVAL 7 DAY)";

        db.query(lastWeekQuery, (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data
                cache.lastWeek = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/districts", (req, res) => {
    // Check if the data is already cached
    if (cache.station_status) {
        res.send(cache.station_status);
    } else {
        db.query("SELECT SUM(available_electric_bikes) AS available_electric_bikes, SUM(available_mechanical_bikes) AS available_mechanical_bikes,district_name FROM station_status WHERE last_update >= NOW() - INTERVAL 9 MINUTE GROUP BY district_name", (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data
                cache.station_status = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/pie_data", (req, res) => {
    // Check if the data is already cached
    if (cache.pie_data) {
        res.send(cache.pie_data);
    } else {
        const pieDataQuery = "SELECT t.district_name AS id, t.district_name AS label, SUM(t.available_bikes) AS value, t.last_update FROM station_status t INNER JOIN (SELECT district_name,MAX(last_update) AS max_last_update FROM station_status GROUP BY district_name) m ON t.district_name = m.district_name AND t.last_update = m.max_last_update GROUP BY t.district_name, t.last_update;";
        db.query(pieDataQuery, (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data
                cache.pie_data = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_information", (req, res) => {
    // Check if the data is already cached
    if (cache.station_information) {
        res.send(cache.station_information);
    } else {
        db.query("SELECT station_id, name, lat, lon, capacity FROM station_information", (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data
                cache.station_information = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_information/paris", (req, res) => {
    // Check if the data is already cached
    if (cache.station_information) {
        res.send(cache.station_information);
    } else {
        db.query("SELECT station_information.station_id, name, lat, lon, capacity, available_docks, available_electric_bikes, \n" +
            "    available_mechanical_bikes, available_bikes, status, MAX(last_update) as last_update,district_name FROM station_information,station_status WHERE \n" +
            "    station_information.station_id = station_status.station_id AND district_name = 'Paris' GROUP BY station_information.station_id", (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data
                cache.station_information = result;
                res.send(result);
            }
        });
    }
});

/* ELECTRIC & MECHANICAL BIKES */

// Last update

app.get("/station_status/bikes/electric/realtime/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `electric_${districtName}`; // Unique cache key for electric bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT SUM(t.available_electric_bikes) AS value, t.last_update FROM station_status t INNER JOIN (SELECT district_name,MAX(last_update) AS max_last_update FROM station_status GROUP BY district_name) m ON t.district_name = m.district_name AND t.last_update = m.max_last_update WHERE t.district_name = ? GROUP BY t.district_name, t.last_update;";
        db.query(bikesQuery, [districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/bikes/mechanical/realtime/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `mechanical_${districtName}`; // Unique cache key for mechanical bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT SUM(t.available_mechanical_bikes) AS value, t.last_update FROM station_status t INNER JOIN (SELECT district_name,MAX(last_update) AS max_last_update FROM station_status GROUP BY district_name) m ON t.district_name = m.district_name AND t.last_update = m.max_last_update WHERE t.district_name = ? GROUP BY t.district_name, t.last_update;";
        db.query(bikesQuery, [districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

// Last day

app.get("/station_status/bikes/electric/last_day/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `electric_day_${districtName}`; // Unique cache key for electric bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT AVG(total_available_electric_bikes) AS value\n" +
            "FROM (\n" +
            "    SELECT SUM(available_electric_bikes) AS total_available_electric_bikes\n" +
            "    FROM station_status\n" +
            "    WHERE district_name = ?\n" +
            "      AND DATE(last_update) = CURDATE() - INTERVAL 1 DAY\n" +
            "    GROUP BY station_id\n" +
            ") AS subquery;";
        db.query(bikesQuery, [districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/bikes/mechanical/last_day/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `mechanical_day_${districtName}`; // Unique cache key for mechanical bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT AVG(total_available_mechanical_bikes) AS value\n" +
            "FROM (\n" +
            "    SELECT SUM(available_mechanical_bikes) AS total_available_mechanical_bikes\n" +
            "    FROM station_status\n" +
            "    WHERE district_name = ?\n" +
            "      AND DATE(last_update) = CURDATE() - INTERVAL 1 DAY\n" +
            "    GROUP BY station_id\n" +
            ") AS subquery;";
        db.query(bikesQuery, [districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

// Last 48 hours
app.get("/station_status/bikes/electric/last_48_hours/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `electric_48_hours_${districtName}`; // Unique cache key for electric bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT AVG(total_available_electric_bikes) AS value\n" +
            "FROM (\n" +
            "    SELECT SUM(available_electric_bikes) AS total_available_electric_bikes\n" +
            "    FROM station_status\n" +
            "    WHERE district_name = ?\n" +
            "      AND last_update >= NOW() - INTERVAL 48 HOUR\n" +
            "    GROUP BY station_id\n" +
            ") AS subquery;";
        db.query(bikesQuery, [districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/bikes/mechanical/last_48_hours/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `mechanical_48_hours_${districtName}`; // Unique cache key for mechanical bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT AVG(total_available_mechanical_bikes) AS value\n" +
            "FROM (\n" +
            "    SELECT SUM(available_mechanical_bikes) AS total_available_mechanical_bikes\n" +
            "    FROM station_status\n" +
            "    WHERE district_name = ?\n" +
            "      AND last_update >= NOW() - INTERVAL 48 HOUR\n" +
            "    GROUP BY station_id\n" +
            ") AS subquery;";
        db.query(bikesQuery, [districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

// Last 72 hours
app.get("/station_status/bikes/electric/last_72_hours/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `electric_72_hours_${districtName}`; // Unique cache key for electric bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT AVG(total_available_electric_bikes) AS value\n" +
            "FROM (\n" +
            "    SELECT SUM(available_electric_bikes) AS total_available_electric_bikes\n" +
            "    FROM station_status\n" +
            "    WHERE district_name = ?\n" +
            "      AND last_update >= NOW() - INTERVAL 72 HOUR\n" +
            "    GROUP BY station_id\n" +
            ") AS subquery;";
        db.query(bikesQuery, [districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/bikes/mechanical/last_72_hours/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `mechanical_72_hours_${districtName}`; // Unique cache key for mechanical bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT AVG(total_available_mechanical_bikes) AS value\n" +
            "FROM (\n" +
            "    SELECT SUM(available_mechanical_bikes) AS total_available_mechanical_bikes\n" +
            "    FROM station_status\n" +
            "    WHERE district_name = ?\n" +
            "      AND last_update >= NOW() - INTERVAL 72 HOUR\n" +
            "    GROUP BY station_id\n" +
            ") AS subquery;";
        db.query(bikesQuery, [districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

// Last week
app.get("/station_status/bikes/electric/last_week/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `electric_last_week_${districtName}`; // Unique cache key for electric bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT AVG(total_available_electric_bikes) AS value\n" +
            "FROM (\n" +
            "    SELECT SUM(available_electric_bikes) AS total_available_electric_bikes\n" +
            "    FROM station_status\n" +
            "    WHERE district_name = ?\n" +
            "      AND last_update >= NOW() - INTERVAL 1 WEEK\n" +
            "    GROUP BY station_id\n" +
            ") AS subquery;";
        db.query(bikesQuery, [districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/bikes/mechanical/last_week/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `mechanical_last_week_${districtName}`; // Unique cache key for mechanical bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT AVG(total_available_mechanical_bikes) AS value\n" +
            "FROM (\n" +
            "    SELECT SUM(available_mechanical_bikes) AS total_available_mechanical_bikes\n" +
            "    FROM station_status\n" +
            "    WHERE district_name = ?\n" +
            "      AND last_update >= NOW() - INTERVAL 1 WEEK\n" +
            "    GROUP BY station_id\n" +
            ") AS subquery;";
        db.query(bikesQuery, [districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

/* Districts list names */

app.get("/station_status/districts/list", (req, res) => {
    // Check if the data is already cached
    if (cache.districts_list) {
        res.send(cache.districts_list);
    } else {
        db.query("SELECT DISTINCT district_name FROM station_status", (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data
                cache.districts_list = result;
                res.send(result);
            }
        });
    }
});

/* Line Chart */

app.get("/station_status/bikes_count", (req, res) => {
    // Check if the data is already cached
    if (cache.bikes_count) {
        res.send(cache.bikes_count);
    }
    else {
        // Cache the data
        const bikesQuery = "SELECT 'Electric bikes' AS id, SUM(available_electric_bikes) AS total_available_bikes, DATE_FORMAT(last_update, '%Y-%m-%d %H:%i:00') as x\n" +
            "FROM station_status\n" +
            "WHERE last_update >= NOW() - INTERVAL 1 DAY\n" +
            "GROUP BY x\n" +
            "UNION\n" +
            "SELECT 'Mechanical bikes' AS id, SUM(available_mechanical_bikes) AS total_available_bikes, DATE_FORMAT(last_update, '%Y-%m-%d %H:%i:00') as x\n" +
            "FROM station_status\n" +
            "WHERE last_update >= NOW() - INTERVAL 1 DAY\n" +
            "GROUP BY x\n" +
            "ORDER BY x ASC;";

        db.query(bikesQuery, (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data
                cache.bikes_count = result;
                res.send(result);
            }
        });
    }
});

// Pie Chart
app.get("/station_status/bikes/electric/forall", (req, res) => {
    const cacheKey = `electric_forall`; // Unique cache key for electric bikes
    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT SUM(available_electric_bikes) AS value FROM `station_status` WHERE last_update >= NOW() - INTERVAL 9 MINUTE";
        db.query(bikesQuery, [], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/bikes/mechanical/forall", (req, res) => {
    const cacheKey = `mechanical_forall`; // Unique cache key for mechanical bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT SUM(available_mechanical_bikes) AS value FROM `station_status` WHERE last_update >= NOW() - INTERVAL 9 MINUTE";
        db.query(bikesQuery, [], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});
app.get("/station_status/status", (req, res) => {
    // Check if the data is already cached
    if (cache.status) {
        res.send(cache.status);
    } else {
        db.query("SELECT COUNT(*) AS count_status FROM `station_status` WHERE status = 1 AND last_update >= NOW() - INTERVAL 9 MINUTE;", (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data
                cache.status = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/count_docks", (req, res) => {
    // Check if the data is already cached
    if (cache.count_docks) {
        res.send(cache.count_docks);
    } else {
        db.query("SELECT SUM(available_docks) AS count_docks FROM `station_status` WHERE status = 1 AND last_update >= NOW() - INTERVAL 9 MINUTE;", (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data
                cache.count_docks = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/count_ebikes", (req, res) => {
    // Check if the data is already cached
    if (cache.count_ebikes) {
        res.send(cache.count_ebikes);
    } else {
        db.query("SELECT SUM(available_electric_bikes) AS count_ebikes FROM `station_status` WHERE status = 1 AND last_update >= NOW() - INTERVAL 9 MINUTE;", (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data
                cache.count_ebikes = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/count_mbikes", (req, res) => {
    // Check if the data is already cached
    if (cache.count_mbikes) {
        res.send(cache.count_mbikes);
    } else {
        db.query("SELECT SUM(available_mechanical_bikes) AS count_mbikes FROM `station_status` WHERE status = 1 AND last_update >= NOW() - INTERVAL 9 MINUTE;", (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data
                cache.count_mbikes = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/bikes_count/realtime/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `line_data_rt${districtName}`; // Unique cache key for electric bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT 'Electric bikes' AS id, SUM(available_electric_bikes) AS total_available_bikes, DATE_FORMAT(last_update, '%Y-%m-%d %H:%i:00') as x\n" +
            "FROM station_status\n" +
            "WHERE last_update >= NOW() - INTERVAL 9 MINUTE\n" +
            "AND district_name = ?\n" +
            "GROUP BY x\n" +
            "UNION\n" +
            "SELECT 'Mechanical bikes' AS id, SUM(available_mechanical_bikes) AS total_available_bikes, DATE_FORMAT(last_update, '%Y-%m-%d %H:%i:00') as x\n" +
            "FROM station_status\n" +
            "WHERE last_update >= NOW() - INTERVAL 9 MINUTE\n" +
            "AND district_name = ?\n" +
            "GROUP BY x\n" +
            "ORDER BY x ASC;";
        db.query(bikesQuery, [districtName,districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/bikes_count/last_day/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `line_data_ld${districtName}`; // Unique cache key for electric bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT 'Electric bikes' AS id, SUM(available_electric_bikes) AS total_available_bikes, DATE_FORMAT(last_update, '%Y-%m-%d %H:%i:00') as x\n" +
            "FROM station_status\n" +
            "WHERE last_update >= NOW() - INTERVAL 1 DAY\n" +
            "AND district_name = ?\n" +
            "GROUP BY x\n" +
            "UNION\n" +
            "SELECT 'Mechanical bikes' AS id, SUM(available_mechanical_bikes) AS total_available_bikes, DATE_FORMAT(last_update, '%Y-%m-%d %H:%i:00') as x\n" +
            "FROM station_status\n" +
            "WHERE last_update >= NOW() - INTERVAL 1 DAY\n" +
            "AND district_name = ?\n" +
            "GROUP BY x\n" +
            "ORDER BY x ASC;";
        db.query(bikesQuery, [districtName,districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/bikes_count/last_48_hours/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `line_data_2d${districtName}`; // Unique cache key for electric bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT 'Electric bikes' AS id, SUM(available_electric_bikes) AS total_available_bikes, DATE_FORMAT(last_update, '%Y-%m-%d %H:%i:00') as x\n" +
            "FROM station_status\n" +
            "WHERE last_update >= NOW() - INTERVAL 2 DAY\n" +
            "AND district_name = ? \n" +
            "GROUP BY x\n" +
            "UNION\n" +
            "SELECT 'Mechanical bikes' AS id, SUM(available_mechanical_bikes) AS total_available_bikes, DATE_FORMAT(last_update, '%Y-%m-%d %H:%i:00') as x\n" +
            "FROM station_status\n" +
            "WHERE last_update >= NOW() - INTERVAL 2 DAY\n" +
            "AND district_name = ?\n" +
            "GROUP BY x\n" +
            "ORDER BY x ASC;";
        db.query(bikesQuery, [districtName,districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/bikes_count/last_72_hours/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `line_data_3d${districtName}`; // Unique cache key for electric bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT 'Electric bikes' AS id, SUM(available_electric_bikes) AS total_available_bikes, DATE_FORMAT(last_update, '%Y-%m-%d %H:%i:00') as x\n" +
            "FROM station_status\n" +
            "WHERE last_update >= NOW() - INTERVAL 3 DAY\n" +
            "AND district_name = ?\n" +
            "GROUP BY x\n" +
            "UNION\n" +
            "SELECT 'Mechanical bikes' AS id, SUM(available_mechanical_bikes) AS total_available_bikes, DATE_FORMAT(last_update, '%Y-%m-%d %H:%i:00') as x\n" +
            "FROM station_status\n" +
            "WHERE last_update >= NOW() - INTERVAL 3 DAY\n" +
            "AND district_name = ?\n" +
            "GROUP BY x\n" +
            "ORDER BY x ASC;";
        db.query(bikesQuery, [districtName,districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/bikes_count/last_week/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `line_data_lw${districtName}`; // Unique cache key for electric bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT 'Electric bikes' AS id, SUM(available_electric_bikes) AS total_available_bikes, DATE_FORMAT(last_update, '%Y-%m-%d %H:%i:00') as x\n" +
            "FROM station_status\n" +
            "WHERE last_update >= NOW() - INTERVAL 1 WEEK\n" +
            "AND district_name = ? \n" +
            "GROUP BY x\n" +
            "UNION\n" +
            "SELECT 'Mechanical bikes' AS id, SUM(available_mechanical_bikes) AS total_available_bikes, DATE_FORMAT(last_update, '%Y-%m-%d %H:%i:00') as x\n" +
            "FROM station_status\n" +
            "WHERE last_update >= NOW() - INTERVAL 1 WEEK\n" +
            "AND district_name = ? \n" +
            "GROUP BY x\n" +
            "ORDER BY x ASC;";
        db.query(bikesQuery, [districtName,districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/districts/realtime/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `bar_data_rt${districtName}`; // Unique cache key for electric bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT SUM(available_electric_bikes) AS available_electric_bikes, SUM(available_mechanical_bikes) AS available_mechanical_bikes,district_name FROM station_status WHERE last_update >= NOW() - INTERVAL 9 MINUTE AND district_name = ? GROUP BY district_name";
        db.query(bikesQuery, [districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});


app.get("/station_status/districts/realtime/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `bar_data_rt${districtName}`; // Unique cache key for electric bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT SUM(available_electric_bikes) AS available_electric_bikes, SUM(available_mechanical_bikes) AS available_mechanical_bikes,district_name FROM station_status WHERE last_update >= NOW() - INTERVAL 1 DAY AND district_name = ? GROUP BY district_name";
        db.query(bikesQuery, [districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/districts/last_48_hours/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `bar_data_rt${districtName}`; // Unique cache key for electric bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT SUM(available_electric_bikes) AS available_electric_bikes, SUM(available_mechanical_bikes) AS available_mechanical_bikes,district_name FROM station_status WHERE last_update >= NOW() - INTERVAL 2 DAY AND district_name = ? GROUP BY district_name";
        db.query(bikesQuery, [districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/districts/last_72_hours/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `bar_data_rt${districtName}`; // Unique cache key for electric bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT SUM(available_electric_bikes) AS available_electric_bikes, SUM(available_mechanical_bikes) AS available_mechanical_bikes,district_name FROM station_status WHERE last_update >= NOW() - INTERVAL 3 DAY AND district_name = ? GROUP BY district_name";
        db.query(bikesQuery, [districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

app.get("/station_status/districts/last_week/:district_name", (req, res) => {
    const districtName = req.params.district_name;
    const cacheKey = `bar_data_rt${districtName}`; // Unique cache key for electric bikes

    // Check if the data is already cached
    if (cache[cacheKey]) {
        res.send(cache[cacheKey]);
    } else {
        const bikesQuery = "SELECT SUM(available_electric_bikes) AS available_electric_bikes, SUM(available_mechanical_bikes) AS available_mechanical_bikes,district_name FROM station_status WHERE last_update >= NOW() - INTERVAL 7 DAY AND district_name = ? GROUP BY district_name";
        db.query(bikesQuery, [districtName], (err, result) => {
            if (err) {
                console.log(err);
                res.status(500).send("Internal Server Error");
            } else {
                // Cache the data with the unique cache key
                cache[cacheKey] = result;
                res.send(result);
            }
        });
    }
});

app.listen(PORT, () => {
    console.log('Connected to server');
    console.log(`Server is running on ${PORT}`);
});