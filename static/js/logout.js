$(document).ready(()=>{
    function get_cookie(name) {
        return document.cookie.split(";").some((c) => {
          return c.trim().startsWith(name + "=");
        });
      }
    function delete_cookie(name, path, domain) {
        if (get_cookie(name)) {
          domain_full = window.location.href.split("/");

          document.cookie =
            name +
            "=" +
            (path ? ";path=" + path : "") +
            (domain
              ? ";domain=" +
                domain_full[2].replace(":", "").replace(/^\d+$/, "")
              : "") +
            ";expires=Thu, 01 Jan 1970 00:00:01 GMT";
        }
      }
    $("#logout").on('click', ()=>{
        $.ajax({
            url: "/api/auth/logout",
            type: "POST",
            success: (res) => {
              delete_cookie("access_token_cookie", "/");
              return Swal.fire({
                icon: "success",
                title: "LOGOUT SUCCESS",
                text: "See You Next Time !",
              }).then(() => {
                window.location.href = "/";
              });
            },
            error: (res) => {
              return res;
            },
          });
    })
})