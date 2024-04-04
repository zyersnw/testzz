    function searchComments() {
        // 검색어 입력란과 선택된 검색 옵션을 가져옵니다.
        var input = document.getElementById('commentSearchInput').value.toLowerCase();
        var option = document.getElementById('searchOption').value;

        // 모든 행(tr)을 가져와서 반복합니다.
        var rows = document.getElementsByTagName('tr');
        for (var i = 0; i < rows.length; i++) {
            var row = rows[i];

            // 각 행에서 검색 대상 열(td)을 가져옵니다.
            var targetCell;
            if (option === 'postTitle') {
                targetCell = row.getElementsByTagName('td')[1]; // 글 제목 열
            } else if (option === 'postAuthor') {
                targetCell = row.getElementsByTagName('td')[2]; // 글 작성자 열
            } else if (option === 'commentContent') {
                targetCell = row.getElementsByTagName('td')[3]; // 댓글 내용 열
            } else if (option === 'commentAuthor') {
                targetCell = row.getElementsByTagName('td')[4]; // 댓글 작성자 열
            }

            // 검색 대상 열이 존재하고 입력한 검색어와 일치하지 않으면 해당 행을 숨깁니다.
            if (targetCell && targetCell.textContent.toLowerCase().indexOf(input) === -1) {
                row.style.display = 'none';
            } else {
                row.style.display = ''; // 일치하면 행을 보여줍니다.
            }
        }
    }


