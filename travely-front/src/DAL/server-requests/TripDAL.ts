import { backendServiceInstance } from './AxiosInstances';

// example to server request by the axios instances
export const sendTripInformation = async (tripInfo: string): Promise<any> => {
    try {
        const response = await backendServiceInstance.post<any>('/', { tripInfo });
        return response.data;
    } catch (error) {
        throw error;
    }
};
