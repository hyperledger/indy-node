
export function randomString(len: number = 6) {
    return (Math.random() + 1).toString(36).substring(len)
}

export function delay(ms: number) {
    return new Promise((resolve) => setTimeout(resolve, ms))
}
