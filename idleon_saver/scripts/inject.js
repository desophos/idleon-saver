async function topLevel() {
    const getFirebaseData = async () => {
        const fb = window.frames[0].firebase
        const uid = fb.auth().currentUser.uid
        const data = await fb.firestore().collection("_data").doc(uid).get().then(doc => doc.data())
        const names = await fb.database().ref().child("_uid").child(uid).once("value").then(res => res.val())
        data.PlayerNames = names
        return data
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