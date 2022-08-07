import express, {Application, Request, Response} from 'express';
import {altairExpress} from 'altair-express-middleware';

const app: Application = express();

// Mount your altair GraphQL client
app.use('/altair', altairExpress({
    endpointURL: 'http://localhost:5000/classlist_api/',
    subscriptionsEndpoint: `ws://localhost:4000/subscriptions`,
    initialQuery: `{ getData { id name surname } }`,
}));

// Redirect all other routes (PLEASE AT THE END OF WORKING ROUTES)
app.use('*', (req: Request, res: Response) => {
    res.redirect("http://localhost:5000");
});

app.listen(3000, () => console.log('Server running'));