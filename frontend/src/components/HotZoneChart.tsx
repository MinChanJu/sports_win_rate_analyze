import * as d3 from "d3";

import React, { useEffect, useRef } from "react";

// =================================================================
// 🏀 타입 정의
// =================================================================
// 각 구역(Zone)의 데이터 인터페이스
interface ZoneData {
  zone: string; // 구역 ID (예: "rim", "three_left_corner")
  percentage: number; // 성공률 (0 ~ 100)
}

// 컴포넌트 Props 인터페이스
interface HotZoneChartProps {
  data: ZoneData[]; // 구역별 데이터 배열
  width: number; // 차트 너비
  height?: number; // 차트 높이 (생략 시 너비에 맞춰 자동 비율 계산)
}

// =================================================================
// 🏀 HotZoneChart 컴포넌트
// =================================================================
const HotZoneChart: React.FC<HotZoneChartProps> = ({ data, width, height }) => {
  // SVG 엘리먼트에 접근하기 위한 ref
  const svgRef = useRef<SVGSVGElement | null>(null);

  // 컴포넌트가 마운트되거나 props가 변경될 때 실행
  useEffect(() => {
    // svgRef가 연결되지 않았거나 데이터가 없으면 중단
    if (!svgRef.current || !data) return;

    // D3를 사용하여 SVG 선택
    const svg = d3.select(svgRef.current);
    // 기존에 그려진 내용 모두 지우기 (재렌더링 시 중복 방지)
    svg.selectAll("*").remove();

    // 📏 코트 규격 및 스케일 설정
    // 실제 비율에 맞춘 가상의 코트 크기 (좌표계 기준)
    const courtWidth = 500;
    const courtHeight = 470; // 반코트 높이 비율 고려

    // 입력받은 width를 기준으로 스케일 계산
    const scale = width / courtWidth;
    // height가 입력되지 않았으면 비율에 맞춰 자동 계산
    const actualHeight = height || courtHeight * scale;

    // SVG 속성 설정
    svg
      .attr("width", width)
      .attr("height", actualHeight)
      // viewBox를 설정하여 반응형으로 만듦 (가상 좌표계 -> 실제 픽셀 매핑)
      .attr("viewBox", `0 0 ${courtWidth} ${courtHeight}`);

    // 🎨 색상 스케일 설정
    // 성공률(0~100%)에 따라 색상을 매핑하는 선형 스케일
    const colorScale = d3
      .scaleLinear<string>()
      // 구간: 0% (파랑) -> 30% (연파랑) -> 50% (흰색) -> 100% (주황/빨강)
      .domain([0, 30, 50, 100])
      // 이미지와 유사한 색상 코드 적용
      .range(["#5b9bd5", "#9dc3e6", "#ffffff", "#ed7d31"]);

    // =================================================================
    // ✅ [핵심] 14개 구역(Zone) 경로(Path) 정의
    // =================================================================
    // 이미지와 정확히 일치하는 영역을 D3 Path 문자열로 정의합니다.
    // 좌표 기준: 왼쪽 상단 (0,0), 골대 밑 중앙 (250, 470)
    const zones = [
      // --- 1. 골밑 (Rim) ---
      { id: "rim", path: "M 190,470 A 60 60 0 0 1 310,470 L 310,390 A 60 60 0 0 0 190,390 Z" },

      // --- 2. 페인트존 상단 (Upper Paint) ---
      { id: "paint_upper", path: "M 190,390 A 60 60 0 0 1 310,390 L 310,290 A 60 60 0 0 0 190,290 Z" },

      // --- 3. 미드레인지 (Mid-Range) 4구역 ---
      // 왼쪽 하단
      { id: "mid_left_low", path: "M 40,470 L 190,470 L 190,390 A 60 60 0 0 1 105,320 L 40,320 Z" },
      // 오른쪽 하단
      { id: "mid_right_low", path: "M 310,470 L 460,470 L 460,320 L 395,320 A 60 60 0 0 1 310,390 Z" },
      // 왼쪽 상단
      { id: "mid_left_high", path: "M 40,320 L 105,320 A 60 60 0 0 1 190,290 L 190,200 L 40,200 Z" },
      // 오른쪽 상단
      { id: "mid_right_high", path: "M 310,290 A 60 60 0 0 1 395,320 L 460,320 L 460,200 L 310,200 Z" },

      // --- 4. 3점슛 (3-Point) 8구역 ---
      // 왼쪽 코너
      { id: "three_left_corner", path: "M 0,470 L 40,470 L 40,200 L 0,200 Z" },
      // 오른쪽 코너
      { id: "three_right_corner", path: "M 460,470 L 500,470 L 500,200 L 460,200 Z" },
      // 왼쪽 윙 (하단)
      { id: "three_left_wing_low", path: "M 0,200 L 40,200 L 40,90 L 0,90 Z" },
      // 오른쪽 윙 (하단)
      { id: "three_right_wing_low", path: "M 460,200 L 500,200 L 500,90 L 460,90 Z" },
      // 왼쪽 탑 (상단)
      { id: "three_left_top", path: "M 0,90 L 190,90 L 190,0 L 0,0 Z" },
      // 오른쪽 탑 (상단)
      { id: "three_right_top", path: "M 310,90 L 500,90 L 500,0 L 310,0 Z" },
      // 중앙 탑 (왼쪽)
      { id: "three_center_left", path: "M 190,200 L 190,90 L 250,90 L 250,200 Z" },
      // 중앙 탑 (오른쪽)
      { id: "three_center_right", path: "M 250,200 L 250,90 L 310,90 L 310,200 Z" },
    ];

    // =================================================================
    // ✅ 5. 구역 그리기 및 데이터 바인딩
    // =================================================================
    zones.forEach((zone) => {
      // props로 전달받은 data에서 현재 구역에 해당하는 데이터를 찾음
      const zoneData = data.find((d) => d.zone === zone.id);
      // 데이터가 없으면 성공률 0%로 처리
      const percentage = zoneData ? zoneData.percentage : 0;
      // 성공률에 맞는 채우기 색상 계산
      const fillColor = colorScale(percentage);

      // ▶️ Path 그리기
      svg
        .append("path")
        .attr("d", zone.path) // 구역 경로
        .attr("fill", fillColor) // 계산된 색상으로 채우기
        .attr("stroke", "white") // 구역 경계선은 흰색
        .attr("stroke-width", 2); // 경계선 두께

      // ▶️ 텍스트 중심점 계산
      // D3의 getBBox()를 사용하여 현재 Path의 경계 상자를 구함
      const pathElement = svg.select(`path[d="${zone.path}"]`).node() as SVGPathElement;
      const bbox = pathElement.getBBox();
      const centroidX = bbox.x + bbox.width / 2;
      const centroidY = bbox.y + bbox.height / 2;

      // ▶️ 성공률 텍스트 표시
      svg
        .append("text")
        .attr("x", centroidX) // 계산된 중심 X 좌표
        .attr("y", centroidY) // 계산된 중심 Y 좌표
        .attr("text-anchor", "middle") // 가로 중앙 정렬
        .attr("dominant-baseline", "middle") // 세로 중앙 정렬
        .attr("fill", "black") // 글자색
        .attr("font-size", "14px") // 글자 크기
        .attr("font-weight", "bold") // 글자 굵기
        // 데이터가 있을 경우에만 소수점 1자리까지 % 표시
        .text(zoneData ? `${percentage.toFixed(1)}%` : "");
    });

    // =================================================================
    // ✅ 6. 코트 라인 덧그리기 (시각적 완성도)
    // =================================================================
    // 구역 위에 흰색 굵은 선으로 코트 라인을 그려서 깔끔하게 마감합니다.
    const lineGroup = svg.append("g").attr("stroke", "white").attr("stroke-width", 3).attr("fill", "none");

    // 3점 라인 (거대한 아크)
    lineGroup.append("path").attr("d", "M 40,470 L 40,200 A 210 210 0 0 1 460,200 L 460,470");

    // 페인트존 박스 (직사각형)
    lineGroup.append("rect").attr("x", 190).attr("y", 290).attr("width", 120).attr("height", 180);

    // 자유투 라인 반원 (점선 효과)
    lineGroup.append("path").attr("d", "M 190,290 A 60 60 0 0 1 310,290").attr("stroke-dasharray", "10,10");

    // 골대 (백보드 및 림)
    lineGroup.append("line").attr("x1", 220).attr("y1", 460).attr("x2", 280).attr("y2", 460); // 백보드
    lineGroup.append("circle").attr("cx", 250).attr("cy", 460).attr("r", 8).attr("fill", "none"); // 림
  }, [data, width, height]); // 의존성 배열: 데이터나 크기가 변경되면 재렌더링

  // SVG 엘리먼트 반환 (ref 연결)
  return <svg ref={svgRef} />;
};

export default HotZoneChart;
