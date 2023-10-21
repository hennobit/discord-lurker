import express from 'express';
import cors from 'cors';
import heartbeatRouter from './routes/heartbeat'; 
import runningSinceRouter from './routes/runningSince';
import usersRouter from './routes/users';
import downtimes from './routes/downtimes';
import bodyParser from 'body-parser';

const app = express();

app.use(cors());
app.use(bodyParser.json());

app.use(heartbeatRouter)
app.use(runningSinceRouter)
app.use(usersRouter)
app.use(downtimes)

app.listen(3000, () => {
    console.log('Server listening on port 3000');
});
