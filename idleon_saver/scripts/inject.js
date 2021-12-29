async function topLevel() {
    const getFirebaseData = async () => {
        const fb = window.frames[0].firebase
        const uid = fb.auth().currentUser.uid
        const docPromise = fb.firestore().doc("_data/" + uid).get()
        return await docPromise.then(doc => doc.data())
    }

    // https://solutional.ee/blog/2020-11-19-Proper-Retry-in-JavaScript.html
    const retry = async (fn, maxAttempts) => {
        const delay = (fn, ms) => new Promise((resolve) => setTimeout(() => resolve(fn()), ms))
        const execute = async (attempt) => {
            try {
                return await fn()
            } catch (err) {
                if (attempt <= maxAttempts) {
                    console.error(`Retrying after 1 second due to:`, err)
                    return delay(() => execute(attempt + 1), 1000)
                } else {
                    throw err
                }
            }
        }
        return execute(1)
    }

    return await retry(getFirebaseData, 10)
}