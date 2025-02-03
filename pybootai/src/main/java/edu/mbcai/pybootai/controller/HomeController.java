package edu.mbcai.pybootai.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class HomeController {

    @GetMapping("/")
    public String home() {

        return "index"; // index -> resouces/templates/index.html로 찾아간다.

    }// http://localhost:80/    으로 들어올때 반응하는 컨트롤러 -> 테스트 완료~

}
