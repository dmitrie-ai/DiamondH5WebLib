export type Domain = [number, number];
export function getDomain(dataArray:number[]):Domain{
    let min =Math.min.apply(false, dataArray)
    let max =Math.max.apply(false, dataArray)
    return [min,max] as Domain
}