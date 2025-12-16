export function parseCSV(data: string) {
  const values = data.split("\n").map((line) => line.trim().split(","));
  return {
    columns: values[0],
    data: values.splice(1),
  };
}
