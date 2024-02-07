// smeeClient.js
const SmeeClient = require('smee-client')

const smee = new SmeeClient({
    source: 'https://smee.io/Wpx6fSOaWjEaOK',
    target: 'http://127.0.0.1:5000',
    logger: console
})

const events = smee.start()

// You can add logic here to stop forwarding events when needed
// events.close()
