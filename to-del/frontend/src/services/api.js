// Updated api.js with Ticket Management and Fallback Queries

import axios from 'axios';

/**
 * Create a pre-configured instance of axios.
 * This instance will automatically use the base URL defined in the .env file,
 * simplifying API calls throughout the application.
 */
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
});

// --- Dashboard ---

/**
 * Fetches high-level statistics for the dashboard.
 * @returns {Promise} A promise that resolves to the stats data.
 */
export const getDashboardStats = () => api.get('/dashboard/stats');

/**
 * Fetches fallback queries (queries that couldn't be answered properly).
 * @returns {Promise} A promise that resolves to fallback queries data.
 */
export const getFallbackQueries = () => api.get('/fallback-queries');

// --- Document Management ---

/**
 * Fetches the list of all uploaded documents.
 * @returns {Promise} A promise that resolves to an array of document objects.
 */
export const getDocuments = () => api.get('/documents');

/**
 * Uploads a new document to the server.
 * @param {File} file - The file to be uploaded.
 * @param {Function} onUploadProgress - A callback function to track upload progress.
 * @returns {Promise} A promise that resolves to the server's response.
 */
export const uploadDocument = (file, onUploadProgress) => {
  const formData = new FormData();
  formData.append('file', file);
  
  return api.post('/documents', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress,
  });
};

/**
 * Deletes a document from the server.
 * @param {string} filename - The name of the file to delete.
 * @returns {Promise} A promise that resolves to the server's response.
 */
export const deleteDocument = (filename) => api.delete(`/documents/${filename}`);

// --- FAQ Management ---

/**
 * Fetches all FAQs from the server.
 * @returns {Promise} A promise that resolves to an array of FAQ objects.
 */
export const getFaqs = () => api.get('/faqs');

/**
 * Creates a new FAQ.
 * @param {object} faqData - The data for the new FAQ { question, answer, category, language }.
 * @returns {Promise} A promise that resolves to the newly created FAQ object.
 */
export const createFaq = (faqData) => api.post('/faqs', faqData);

/**
 * Updates an existing FAQ.
 * @param {number} id - The ID of the FAQ to update.
 * @param {object} faqData - The updated FAQ data.
 * @returns {Promise} A promise that resolves to the updated FAQ object.
 */
export const updateFaq = (id, faqData) => api.put(`/faqs/${id}`, faqData);

/**
 * Deletes an FAQ.
 * @param {number} id - The ID of the FAQ to delete.
 * @returns {Promise} A promise that resolves to the server's confirmation response.
 */
export const deleteFaq = (id) => api.delete(`/faqs/${id}`);

// --- Ticket Management ---

/**
 * Fetches all tickets with optional status filtering.
 * @param {string} status - Optional status filter ('open', 'answered', 'closed').
 * @returns {Promise} A promise that resolves to an array of ticket objects.
 */
export const getTickets = (status = '') => {
  const params = status ? { status } : {};
  return api.get('/tickets', { params });
};

/**
 * Fetches a specific ticket by ID.
 * @param {number} ticketId - The ID of the ticket to fetch.
 * @returns {Promise} A promise that resolves to the ticket object.
 */
export const getTicket = (ticketId) => api.get(`/tickets/${ticketId}`);

/**
 * Responds to a ticket with admin response.
 * @param {number} ticketId - The ID of the ticket to respond to.
 * @param {object} responseData - The response data { admin_response }.
 * @returns {Promise} A promise that resolves to the updated ticket object.
 */
export const respondToTicket = (ticketId, responseData) => 
  api.put(`/tickets/${ticketId}/respond`, responseData);

/**
 * Closes a ticket.
 * @param {number} ticketId - The ID of the ticket to close.
 * @returns {Promise} A promise that resolves to the updated ticket object.
 */
export const closeTicket = (ticketId) => api.put(`/tickets/${ticketId}/close`);

/**
 * Deletes a ticket.
 * @param {number} ticketId - The ID of the ticket to delete.
 * @returns {Promise} A promise that resolves to the server's confirmation response.
 */
export const deleteTicket = (ticketId) => api.delete(`/tickets/${ticketId}`);

// --- Conversation Logs ---

/**
 * Fetches conversation logs with optional pagination.
 * @param {number} page - The page number to fetch.
 * @param {number} limit - The number of items per page.
 * @returns {Promise} A promise that resolves to an object containing conversations and pagination info.
 */
export const getConversations = (page = 1, limit = 10) =>
  api.get('/conversations', { params: { page, limit } });

// --- Bot Configuration ---

/**
 * Fetches the current bot configuration.
 * @returns {Promise} A promise that resolves to the configuration object.
 */
export const getBotConfig = () => api.get('/config');

/**
 * Updates the bot configuration.
 * @param {object} configData - The new configuration settings.
 * @returns {Promise} A promise that resolves to the updated configuration object.
 */
export const updateBotConfig = (configData) => api.post('/config', configData);

/**
 * Fetches the HTML embed code snippet for the website widget.
 * @returns {Promise} A promise that resolves to an object containing the embed code.
 */
export const getEmbedCode = () => api.get('/embed-code');