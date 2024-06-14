import { CancelablePromise, listAllConnections, createConnection, GetConnectedAccountResponse, GetConnectedAccountData, CreateConnectionData, CreateConnectionResponse, ListAllConnectionsData, ListAllConnectionsResponse, getConnectedAccount } from "../client";
import { Composio } from "../";

export class ConnectedAccounts {
    constructor(private readonly client: Composio) {
    }

    /**
     * Retrieves a list of all connected accounts in the Composio platform.
     * 
     * It supports pagination and filtering based on various parameters such as app ID, integration ID, and connected account ID. The response includes an array of connection objects, each containing details like the connector ID, connection parameters, status, creation/update timestamps, and associated app information.
     * 
     * @param {ListAllConnectionsData} data The data for the request.
     * @returns {CancelablePromise<ListAllConnectionsResponse>} A promise that resolves to the list of all connected accounts.
     * @throws {ApiError} If the request fails.
     */
    list(data: ListAllConnectionsData = {}): CancelablePromise<ListAllConnectionsResponse> {
        return listAllConnections(data, this.client.config);
    }

    /**
     * Connects an account to the Composio platform.
     * 
     * This method allows you to connect an external app account with Composio. It requires the integration ID in the request body and returns the connection status, connection ID, and a redirect URL (if applicable) for completing the connection flow.
     * 
     * @param {CreateConnectionData} data The data for the request.
     * @returns {CancelablePromise<CreateConnectionResponse>} A promise that resolves to the connection status and details.
     * @throws {ApiError} If the request fails.
     */
    create(data: CreateConnectionData = {}): CancelablePromise<CreateConnectionResponse> {
        return createConnection(data, this.client.config);
    }

    /**
     * Retrieves details of a specific account connected to the Composio platform by providing its connected account ID.
     * 
     * The response includes the integration ID, connection parameters (such as scope, base URL, client ID, token type, access token, etc.), connection ID, status, and creation/update timestamps.
     * 
     * @param {GetConnectedAccountData} data The data for the request.
     * @returns {CancelablePromise<GetConnectedAccountResponse>} A promise that resolves to the details of the connected account.
     * @throws {ApiError} If the request fails.
     */
    get(data: GetConnectedAccountData): CancelablePromise<GetConnectedAccountResponse> {
        return getConnectedAccount(data, this.client.config);
    }

    /**
     * Initiates a new connected account on the Composio platform.
     * 
     * This method allows you to start the process of connecting an external app account with Composio. It requires the integration ID and optionally the entity ID, additional parameters, and a redirect URL.
     * 
     * @param {CreateConnectionData["requestBody"]} data The data for the request.
     * @returns {CancelablePromise<ConnectionRequest>} A promise that resolves to the connection request model.
     * @throws {ApiError} If the request fails.
     */
    async initiate(
        data: CreateConnectionData["requestBody"]
    ): Promise<ConnectionRequest> {
        const response = await createConnection({requestBody: data}, this.client.config);
        return new ConnectionRequest(response.connectionStatus!, response.connectedAccountId!, response.redirectUrl, this.client);
    }
}

export class ConnectionRequest {
    connectionStatus: string;
    connectedAccountId: string;
    redirectUrl: string | null;

    /**
     * Connection request model.
     * @param {string} connectionStatus The status of the connection.
     * @param {string} connectedAccountId The unique identifier of the connected account.
     * @param {string} [redirectUrl] The redirect URL for completing the connection flow.
     */
    constructor(connectionStatus: string, connectedAccountId: string, redirectUrl: string | null = null, private readonly client: Composio) {
        this.connectionStatus = connectionStatus;
        this.connectedAccountId = connectedAccountId;
        this.redirectUrl = redirectUrl;
    }

    /**
     * Save user access data.
     * @param {Composio} client The Composio client instance.
     * @param {Object} data The data to save.
     * @param {Object} data.fieldInputs The field inputs to save.
     * @param {string} [data.redirectUrl] The redirect URL for completing the connection flow.
     * @param {string} [data.entityId] The entity ID associated with the user.
     * @returns {Promise<Object>} The response from the server.
     */
    async saveUserAccessData(data: {
        fieldInputs: Record<string, string>;
        redirectUrl?: string;
        entityId?: string;
    }) {
        const connectedAccount = await this.client.connectedAccounts.get({
            connectedAccountId: this.connectedAccountId,
        });
        return createConnection({
            requestBody: {
                integrationId: connectedAccount.integrationId,
                data: data.fieldInputs,
                redirectUri: data.redirectUrl,
                userUuid: data.entityId,
            }
        }, this.client.config);
    }

    /**
     * Wait until the connection becomes active.
     * @param {Composio} client The Composio client instance.
     * @param {number} [timeout=60] The timeout period in seconds.
     * @returns {Promise<ConnectedAccountModel>} The connected account model.
     * @throws {ComposioClientError} If the connection does not become active within the timeout period.
     */
    async waitUntilActive(timeout = 60) {
        const startTime = Date.now();
        while (Date.now() - startTime < timeout * 1000) {
            const connection = await this.client.connectedAccounts.get({
                connectedAccountId: this.connectedAccountId,
            });
            if (connection.status === 'ACTIVE') {
                return connection;
            }
            await new Promise(resolve => setTimeout(resolve, 1000));
        }

        throw new Error(
            'Connection did not become active within the timeout period.'
        );
    }
}

