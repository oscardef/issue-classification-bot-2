# Use Node.js as the base image
FROM node:20.6.1

# Install smee-client and node-fetch globally
RUN npm install --global smee-client node-fetch

# Expose the default smee port
EXPOSE 3000

# Command to run the smee client
CMD ["smee", "-u", "https://smee.io/Wpx6fSOaWjEaOK", "--port", "3000"]
