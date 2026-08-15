export const seedCourses = [
  ["INT101", "Nhập môn Trí tuệ nhân tạo"],
  ["WEB201", "Lập trình Web"],
  ["DAT102", "Cơ sở dữ liệu"],
  ["NET203", "Mạng máy tính"],
  ["MOB202", "Lập trình ứng dụng di động"]
] as const;

export const seedSections = [
  [1, "INT101", "GV001", "A2-301", 0, 1, "07:00", "07:50"],
  [2, "WEB201", "GV002", "A2-203", 2, 8, "14:25", "15:15"],
  [3, "DAT102", "GV001", "B1-105", 4, 4, "09:50", "10:40"],
  [4, "NET203", "GV003", "A3-202", 1, 3, "08:50", "09:40"],
  [5, "MOB202", "GV002", "A1-405", 3, 10, "16:20", "17:10"]
] as const;

const seedStudents = ["SV001", "SV002", "SV003", "SV004", "SV005", "SV006", "SV007", "SV008"];
export const seedEnrollments = [1, 2, 3, 4, 5].flatMap((sectionId) => seedStudents.map((studentId) => [sectionId, studentId] as const));
